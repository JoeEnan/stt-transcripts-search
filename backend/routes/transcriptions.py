import logging
import os
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from utils.db_operations import (
    db_get_transcriptions,
    db_search_transcriptions,
)
from utils.transcriber import transcribe_files

router = APIRouter(prefix="/api", tags=["transcriptions"])

# Externalize the audio storage path
AUDIO_STORAGE_PATH = os.getenv("AUDIO_STORAGE_PATH", "audio_storage")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    if not all(file.filename.endswith((".wav", ".mp3", ".m4a")) for file in files):
        logger.error("Unsupported file format")
        raise HTTPException(status_code=400, detail="Unsupported file format")

    batch_uuid = await transcribe_files(files, background_tasks, db)

    logger.info(f"Transcription started for batch: {batch_uuid}")
    return JSONResponse(
        content={
            "message": "Files uploaded, transcription started.",
            "batch_uuid": batch_uuid,
        },
        status_code=202,
    )


@router.get("/transcriptions")
async def get_transcriptions(db: Session = Depends(get_db)) -> JSONResponse:
    transcriptions = db_get_transcriptions(db=db)
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
    db: Session = Depends(get_db),
) -> JSONResponse:
    transcriptions = db_search_transcriptions(
        file_name, match_full_file_name, match_case, db=db
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
            for transcription in transcriptions
        ],
        status_code=200,
    )
