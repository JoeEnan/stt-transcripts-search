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
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> JSONResponse:
    if not file.filename.endswith((".wav", ".mp3", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    audio_path = os.path.join(AUDIO_STORAGE_PATH, unique_filename)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Start transcription task
    background_tasks.add_task(
        run_in_threadpool,
        lambda: asyncio.run(transcribe_audio_task(audio_path, file.filename)),
    )

    return JSONResponse(
        content={"message": "File uploaded, transcription started."}, status_code=202
    )


# @router.get("/transcriptions")
# async def get_transcriptions(db: Session = Depends(get_db)):
#     transcriptions = db.query(Transcription).all()
#     return transcriptions


# @router.get("/search")
# async def search(file_name: str, db: Session = Depends(get_db)):
#     results = search_transcriptions(db, file_name)
#     return results
