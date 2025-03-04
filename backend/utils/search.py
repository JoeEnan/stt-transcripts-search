from sqlalchemy.orm import Session

from database import Transcription


def search_transcriptions(db: Session, file_name: str):
    return (
        db.query(Transcription)
        .filter(Transcription.audio_file.like(f"%{file_name}%"))
        .all()
    )
