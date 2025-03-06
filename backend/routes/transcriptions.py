import asyncio
import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from database import SessionLocal, Transcription
from routes.websocket import transcribe_audio_task

router = APIRouter(prefix="/api", tags=["transcriptions"])

AUDIO_STORAGE_PATH = "audio_storage"


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks, files: Annotated[list[UploadFile], File()] = ...
) -> JSONResponse:
    if not all(file.filename.endswith((".wav", ".mp3", ".m4a")) for file in files):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    # Generate a unique UUID for this batch
    batch_uuid = str(uuid.uuid4())

    audio_paths = []
    original_audio_names = []
    for file in files:
        unique_filename = f"{batch_uuid}_{file.filename}"
        audio_path = os.path.join(AUDIO_STORAGE_PATH, unique_filename)
        audio_paths.append(audio_path)
        original_audio_names.append(file.filename)
        async with aiofiles.open(audio_path, "wb") as buffer:
            await buffer.write(await file.read())

    # Start transcription task
    background_tasks.add_task(
        run_in_threadpool,
        lambda: asyncio.run(
            transcribe_audio_task(batch_uuid, audio_paths, original_audio_names)
        ),
    )

    return JSONResponse(
        content={
            "message": "Files uploaded, transcription started.",
            "batch_uuid": batch_uuid,
        },
        status_code=202,
    )


@router.get("/transcriptions")
async def get_transcriptions():
    with SessionLocal() as session:
        transcriptions = session.query(Transcription).all()
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
async def search(file_name: str):
    with SessionLocal() as session:
        results = (
            session.query(Transcription)
            .filter(Transcription.original_audio_filename.like(f"%{file_name}%"))
            .all()
        )
        return JSONResponse(
            content=[
                {
                    "id": transcription.id,
                    "audio_filepath": f"http://localhost:9090/{transcription.audio_filepath}",
                    "original_audio_filename": transcription.original_audio_filename,
                    "text": transcription.text,
                    "created_at": transcription.created_at.isoformat(),
                }
                for transcription in results
            ],
            status_code=200,
        )
