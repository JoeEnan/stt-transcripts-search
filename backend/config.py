import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/transcriptions.db")
    AUDIO_STORAGE_PATH: str = os.getenv("AUDIO_STORAGE_PATH", "audio_storage")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "tiny")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiate and export a single settings instance
settings = Settings()
