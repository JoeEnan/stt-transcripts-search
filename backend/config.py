import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database connection string - default set to a local SQLite database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/transcriptions.db")
    # Path for storing uploaded audio files
    AUDIO_STORAGE_PATH: str = os.getenv("AUDIO_STORAGE_PATH", "audio_storage")
    # Whisper Model Specification
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny")

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# Instantiate and export a single settings instance
settings = Settings()
