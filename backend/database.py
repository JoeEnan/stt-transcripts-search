from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transcription(Base):
    """
    Task 2c i: Use SQLite as the primary database for storing the audio file name,
        transribed text and created timestamp..
    Assumptions:
        - audio file path will be made unique with batch_uuid that is generated per upload
        - original audio file name that is uploaded by the user will be preserved
            - This will then be displayed and used for search.
    """

    __tablename__ = "transcriptions"
    id = Column(Integer, primary_key=True, index=True)
    audio_filepath = Column(String, index=True)
    original_audio_filename = Column(String, index=True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.now().astimezone())


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
