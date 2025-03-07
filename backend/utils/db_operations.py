from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Transcription, get_db


def db_save_transcription(
    audio_filepath: str,
    original_audio_filename: str,
    transcribed_text: str,
    db: Session = Depends(get_db),
) -> None:
    """Save a transcription record to the database using the provided session."""
    transcription = Transcription(
        audio_filepath=audio_filepath,
        original_audio_filename=original_audio_filename,
        text=transcribed_text,
    )
    db.add(transcription)
    db.commit()


def db_get_transcriptions(db: Session = Depends(get_db)):
    """Retrieve all transcriptions from the database."""
    return db.query(Transcription).all()


def db_search_transcriptions(
    file_name: str,
    match_full_file_name=False,
    match_case=False,
    db: Session = Depends(get_db),
):
    """Search for transcriptions based on file name."""
    query = db.query(Transcription)

    if match_full_file_name:
        if match_case:
            query = query.filter(Transcription.original_audio_filename == file_name)
        else:
            query = query.filter(
                func.lower(Transcription.original_audio_filename) == file_name.lower()
            )
    elif match_case:
        query = query.filter(
            Transcription.original_audio_filename.op("GLOB")(f"*{file_name}*")
        )
    else:
        query = query.filter(
            func.lower(Transcription.original_audio_filename).like(
                f"%{file_name.lower()}%"
            )
        )

    return query.all()
