import asyncio
import os
import uuid

import aiofiles
import whisper
from fastapi import BackgroundTasks, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from database import get_db
from log_config import logger
from utils.db_operations import db_get_transcriptions, db_save_transcription
from utils.websocket_manager import get_websockets

model = whisper.load_model("tiny")


async def transcribe_files(
    files, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """Handle the transcription of uploaded audio files."""
    batch_uuid = str(uuid.uuid4())
    audio_paths = []
    original_audio_names = []

    for file in files:
        unique_filename = f"{batch_uuid}_{file.filename}"
        audio_path = os.path.join(
            os.getenv("AUDIO_STORAGE_PATH", "audio_storage"), unique_filename
        )
        audio_paths.append(audio_path)
        original_audio_names.append(file.filename)

        try:
            async with aiofiles.open(audio_path, "wb") as buffer:
                await buffer.write(await file.read())
        except Exception as e:
            raise Exception(f"Error writing file {file.filename}: {e}")

    # Start transcription task
    background_tasks.add_task(
        run_in_threadpool,
        lambda: asyncio.run(
            process_transcription_batch(
                batch_uuid, audio_paths, original_audio_names, db
            )
        ),
    )

    return batch_uuid


async def process_transcription_batch(
    batch_uuid: str,
    file_paths: list[str],
    original_audio_names: list[str],
    db: Session = Depends(get_db),
):
    """Transcribe a batch of audio files and save results to database."""
    results = []
    for file_path, original_audio_name in zip(
        file_paths, original_audio_names, strict=False
    ):
        transcribed_text = transcribe_audio(file_path)
        db_save_transcription(file_path, original_audio_name, transcribed_text, db)
        transcriptions = db_get_transcriptions(db=db)
        logger.info(f"Content {len(transcriptions)}...")
        results.append({"file": original_audio_name})
        # Notify relevant WebSocket clients that transcription is done
        for websocket in get_websockets(batch_uuid):
            try:
                await websocket.send_json(
                    {
                        "status": "completed",
                        "file": original_audio_name,
                        "text": transcribed_text,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to send message over WebSocket: {e}")

    # For batch upload, final batch completion message
    if len(file_paths) > 1:
        for websocket in get_websockets(batch_uuid):
            try:
                await websocket.send_json(
                    {
                        "status": "batch_completed",
                        "total_files": len(file_paths),
                        "results": results,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Failed to send final completion message for batch job over WebSocket: {e}"
                )
    else:
        try:
            await websocket.send_json(
                {
                    "status": "job_completed",
                    "results": results,
                }
            )
        except Exception as e:
            logger.error(
                f"Failed to send final completion message for single job over WebSocket: {e}"
            )


def transcribe_audio(file_path: str) -> str:
    """Transcribe audio using Whisper model."""
    result = model.transcribe(file_path)
    return result["text"]
