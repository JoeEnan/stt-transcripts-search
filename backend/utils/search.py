from database import Transcription
from sqlalchemy.orm import Session


def search_transcriptions(db: Session, file_name: str):
    return (
        db.query(Transcription)
        .filter(Transcription.audio_file.like(f"%{file_name}%"))
        .all()
    )
