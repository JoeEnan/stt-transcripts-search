import asyncio
import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from routes.websocket import transcribe_audio_task

router = APIRouter(prefix="/api", tags=["transcriptions"])

AUDIO_STORAGE_PATH = "backend/audio_storage"
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)
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
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

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


# @router.get("/transcriptions")
# async def get_transcriptions(db: Session = Depends(get_db)):
#     transcriptions = db.query(Transcription).all()
#     return transcriptions


# @router.get("/search")
# async def search(file_name: str, db: Session = Depends(get_db)):
#     results = search_transcriptions(db, file_name)
#     return results
