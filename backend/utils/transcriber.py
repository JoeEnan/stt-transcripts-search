import asyncio
import os
import uuid

import aiofiles
from fastapi import BackgroundTasks, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from log_config import logger
from utils.db_operations import db_save_transcription
from utils.websocket_manager import get_websockets


async def transcribe_files(
    files, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    """
    Mentioned in Task 2a ii and Task 2b ii: POST /transcribe
    - Uploads all files to settings.AUDIO_STORAGE_PATH
    - Once all files are uploaded, send processing jobs to background threads running
        on process_transcription_batch function for processing
            - After each audio file is processed by Whisper, it will be saved to sqlite db.
    - return the batch_uuid to POST /transcribe after sending all processing jobs to workers
    """
    batch_uuid = str(uuid.uuid4())
    audio_paths = []
    original_audio_names = []

    for file in files:
        unique_filename = f"{batch_uuid}_{file.filename}"
        audio_path = os.path.join(settings.AUDIO_STORAGE_PATH, unique_filename)
        audio_paths.append(audio_path)
        original_audio_names.append(file.filename)

        try:
            async with aiofiles.open(audio_path, "wb") as buffer:
                await buffer.write(await file.read())
        except Exception as e:
            msg = f"Error writing file {file.filename}: {e}"
            raise Exception(msg) from e

    # Start transcription task in the background
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
    """
    - Worker threads called with this function will process the audio file through
        transcribe_audio function
    - Once transcript is returned, save the transcript using db_save_transcription function
    - Send out a notification that an audio file has been processed by whisper
        - Status = completed
    - Move on to the next audio file to process
    - For replying, there are different return statuses for single or batch jobs:
        - Single Audio File Upload: Status = job_completed
        - Batch Audio File Upload: Status = batch_completed
    """
    results = []
    for file_path, original_audio_name in zip(
        file_paths, original_audio_names, strict=False
    ):
        transcribed_text = transcribe_audio(file_path)
        db_save_transcription(file_path, original_audio_name, transcribed_text, db)
        results.append({"file": original_audio_name})
        # Notify connected WebSocket clients about the completed transcription
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
        for websocket in get_websockets(batch_uuid):
            try:
                await websocket.send_json(
                    {"status": "job_completed", "results": results}
                )
            except Exception as e:
                logger.error(
                    f"Failed to send final completion message for single job over WebSocket: {e}"
                )


def get_model():
    """
    Load and return the Whisper model.
    In production, this function loads the heavy model.
    In tests, you can monkeypatch this function (or have it return a dummy object)
    so that the openai-whisper library is not actually imported.
    """
    if not hasattr(get_model, "model"):
        import whisper  # heavy dependency, only imported when needed

        get_model.model = whisper.load_model(settings.WHISPER_MODEL)
    return get_model.model


def transcribe_audio(file_path: str, model_instance: object = None) -> str:
    """
    Task 2b i and Task 2b ii: Use the openai/whisper-tiny model from Hugging Face.
    - Transcribe audio from the given file path using the provided model.
    - If no model is given, it loads one using get_model().
    - This allows for easy injection of a mock model in tests.
    - Assumptions:
        - preprocessing of audio such as VAD can be done, but whisper library's dependencies
            itself is already a huge package. Will feed audio files to Whisper for now.
            - VAD: Voice Activity Detection
        - For tasks like voice activity detection, speaker detection, word level timestamps output
            use project: https://github.com/SYSTRAN/faster-whisper
    """
    if model_instance is None:
        model_instance = get_model()
    result = model_instance.transcribe(file_path)
    return result["text"]
