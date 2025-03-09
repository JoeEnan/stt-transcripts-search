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
from log_config import logger
from utils.db_operations import (
    db_get_transcriptions,
    db_search_transcriptions,
)
from utils.transcriber import transcribe_files

router = APIRouter(prefix="/api", tags=["transcriptions"])


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Task 2a ii and Task 2b ii:
    - POST /transcribe: Accepts audio files, performs transcription and save results in database.
    - Implement necessary audio preprocessing
    - Assumptions:
        - Endpoint will only accept wav, mp3 and m4a audio files
        - Assume that files with this extension contains audio content
        - Once all files are passed into transcribe_files function, immediately update frontend
            that all files are saved into audio_storage folder, and are set to be processed by whisper
            - More information in backend/utils/transcriber.py > transcribe_files function
        - batch_uuid is a unique ID for frontend to connect to the websocket hosted by FastAPI that
            informs the frontend on which batch of audio files (one or many) has completed processing.
            - More information in backend/routes/websocket.py
    """
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
    """
    - Task 2a iii:
    - GET /transcriptions: Retrieves all transcriptions from the database.
    - Assumptions:
        - Returns all transcriptions from database:
            - ID of transcription
            - Transcription's audio_filepath - this can be used for frontend to hear the uploaded audio file
                - Mounting of audio_storage folder (which stores the audio files) is done in backend/main.py
            - Original Audio Filename - original audio filename when uploaded by the user
            - transcript output of whisper that is saved
            - transcript creation datetime
    """
    transcriptions = db_get_transcriptions(db=db)
    return JSONResponse(
        content=[
            {
                "id": transcription.id,
                "audio_filepath": f"{transcription.audio_filepath}",
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
    """
    - Task 2a iv:
    - GET /search: Performs a full-text search on transcriptions based on audio file name.
    - Assumptions:
        - Search Based on the file name only
        - Allow for exact full file name and/or case sensitive searches
        - Returns matching transcription in the same format as Task 2a iii.
    """
    transcriptions = db_search_transcriptions(
        file_name, match_full_file_name, match_case, db=db
    )
    return JSONResponse(
        content=[
            {
                "id": transcription.id,
                "audio_filepath": f"{transcription.audio_filepath}",
                "original_audio_filename": transcription.original_audio_filename,
                "text": transcription.text,
                "created_at": transcription.created_at.isoformat(),
            }
            for transcription in transcriptions
        ],
        status_code=200,
    )
