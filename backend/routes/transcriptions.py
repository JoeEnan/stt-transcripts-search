import asyncio
import logging
import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from routes.websocket import transcribe_audio_task
from utils.search import search_transcriptions

router = APIRouter(prefix="/api", tags=["transcriptions"])

# Externalize the audio storage path
AUDIO_STORAGE_PATH = os.getenv("AUDIO_STORAGE_PATH", "audio_storage")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks, files: Annotated[list[UploadFile], File()] = ...
) -> JSONResponse:
    if not all(file.filename.endswith((".wav", ".mp3", ".m4a")) for file in files):
        logger.error("Unsupported file format")
        raise HTTPException(status_code=400, detail="Unsupported file format")

    batch_uuid = str(uuid.uuid4())
    audio_paths = []
    original_audio_names = []

    for file in files:
        unique_filename = f"{batch_uuid}_{file.filename}"
        audio_path = os.path.join(AUDIO_STORAGE_PATH, unique_filename)
        audio_paths.append(audio_path)
        original_audio_names.append(file.filename)

        try:
            async with aiofiles.open(audio_path, "wb") as buffer:
                await buffer.write(await file.read())
        except Exception as e:
            logger.exception(f"Error writing file {file.filename}: {e}")
            raise HTTPException(status_code=500, detail="Error saving file") from e

    # Start transcription task
    background_tasks.add_task(
        run_in_threadpool,
        lambda: asyncio.run(
            transcribe_audio_task(batch_uuid, audio_paths, original_audio_names)
        ),
    )

    logger.info(f"Transcription started for batch: {batch_uuid}")
    return JSONResponse(
        content={
            "message": "Files uploaded, transcription started.",
            "batch_uuid": batch_uuid,
        },
        status_code=202,
    )


@router.get("/transcriptions")
async def get_transcriptions():
    transcriptions = search_transcriptions(file_name="")
    return JSONResponse(
        content=[
            {
                "id": transcription.id,
                "audio_filepath": f"http://localhost:9090/{transcription.audio_filepath}",
                "original_audio_filename": transcription.original_audio_filename,
                "text": transcription.text,
                "created_at": transcription.created_at.isoformat(),
            }
            for transcription in transcriptions
        ],
        status_code=200,
    )


@router.get("/search")
async def search(
    file_name: str,
    match_full_file_name: Annotated[
        bool, Query(description="Match full file name only")
    ] = False,
    match_case: Annotated[bool, Query(description="Match case sensitive")] = False,
):
    transcriptions = search_transcriptions(file_name, match_full_file_name, match_case)
    return JSONResponse(
        content=[
            {
                "id": transcription.id,
                "audio_filepath": f"http://localhost:9090/{transcription.audio_filepath}",
                "original_audio_filename": transcription.original_audio_filename,
                "text": transcription.text,
                "created_at": transcription.created_at.isoformat(),
            }
            for transcription in transcriptions
        ],
        status_code=200,
    )
