import os
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./backend/data/transcriptions.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transcription(Base):
    __tablename__ = "transcriptions"
    id = Column(Integer, primary_key=True, index=True)
    audio_filename = Column(String, index=True)
    original_audio_filename = Column(String, index=True)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.now(UTC))


def init_db():
    if not os.path.isfile("transcriptions.db"):
        Base.metadata.create_all(bind=engine)
