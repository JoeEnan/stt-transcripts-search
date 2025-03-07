import asyncio
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Transcription
from utils import db_operations, transcriber
from utils.websocket_manager import (
    add_websocket,
    clear_websockets,
    remove_websocket,
)

# Set the environment variable for the in-memory database
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


# -------------------------------
# Fixtures for in-memory database
# -------------------------------
@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(
        os.getenv("DATABASE_URL"),
        connect_args={"check_same_thread": False},
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def setup_database(test_engine):
    # Create all tables before any tests run and drop them afterward.
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_engine):
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionTesting()
    # Clear the transcriptions table before each test.
    session.query(Transcription).delete()
    session.commit()
    yield session
    session.close()


# -------------------------------
# Tests for transcriber.py
# -------------------------------
def test_transcribe_audio(monkeypatch):
    """
    Test transcribe_audio by monkey-patching the whisper model's transcribe method.
    """
    # Monkey-patch the transcribe method on the model to return a dummy response.
    monkeypatch.setattr(
        transcriber.model, "transcribe", lambda fp: {"text": "dummy transcribed text"}
    )
    result = transcriber.transcribe_audio("dummy_audio_path.mp3")
    assert result == "dummy transcribed text"


# Create a dummy websocket that simply collects messages that are sent.
class DummyWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.closed = False

    async def send_json(self, message):
        self.sent_messages.append(message)

    async def close(self):
        self.closed = True


# Unit test for process_transcription_batch
@pytest.mark.asyncio
async def test_process_transcription_batch(db_session, monkeypatch):
    clear_websockets()  # Ensure no leftover websockets from previous tests.

    # Monkey-patch transcribe_audio to return a fixed string regardless of file.
    monkeypatch.setattr(
        transcriber.model, "transcribe", lambda fp: {"text": "unit-test transcription"}
    )

    # Use dummy websocket for a given batch_uuid.
    batch_uuid = "test_batch"
    dummy_ws = DummyWebSocket()
    add_websocket(batch_uuid, dummy_ws)

    # Prepare file paths and original names.
    file_paths = ["audio/test1.mp3", "audio/test2.mp3"]
    original_audio_names = ["test1.mp3", "test2.mp3"]

    # Run the transcription batch process.
    await transcriber.process_transcription_batch(
        batch_uuid, file_paths, original_audio_names, db_session
    )

    # Let the event loop run a bit to ensure all awaitables are handled.
    await asyncio.sleep(0)

    # Verify that records have been inserted (should be 2 new records).
    records = db_operations.db_get_transcriptions(db_session)
    assert len(records) == 2

    # Verify dummy websocket received messages.
    # Since there are 2 files, we expect two "completed" messages and one final "batch_completed" message.
    msgs = dummy_ws.sent_messages
    completed_msgs = [msg for msg in msgs if msg.get("status") == "completed"]
    batch_completed_msgs = [
        msg for msg in msgs if msg.get("status") == "batch_completed"
    ]

    assert len(completed_msgs) == 2, (
        f"Expected 2 completed messages but got: {completed_msgs}"
    )
    assert len(batch_completed_msgs) == 1, (
        f"Expected 1 batch_completed message but got: {batch_completed_msgs}"
    )

    # Remove the dummy websocket once done.
    remove_websocket(batch_uuid, dummy_ws)


# -------------------------------
# Tests for db_operations.py
# -------------------------------
def test_db_save_and_get_transcriptions(db_session):
    """
    Test that db_save_transcription saves a record and db_get_transcriptions retrieves it.
    """
    # Save a transcription using the db_operations helper.
    db_operations.db_save_transcription(
        audio_filepath="audio/path.mp3",
        original_audio_filename="original.mp3",
        transcribed_text="Test transcription",
        db=db_session,
    )

    records = db_operations.db_get_transcriptions(db_session)
    assert len(records) == 1
    record = records[0]
    assert record.audio_filepath == "audio/path.mp3"
    assert record.original_audio_filename == "original.mp3"
    assert record.text == "Test transcription"


def test_db_search_transcriptions(db_session):
    """
    Test various scenarios of searching transcriptions.
    """
    # First, insert multiple records.
    db_operations.db_save_transcription(
        "audio1.mp3", "Sample1.mp3", "text 1", db=db_session
    )
    db_operations.db_save_transcription(
        "audio2.mp3", "sample2.mp3", "text 2", db=db_session
    )
    db_operations.db_save_transcription(
        "audio3.mp3", "another_sample.MP3", "text 3", db=db_session
    )

    # Test partial search (case-insensitive).
    results_partial = db_operations.db_search_transcriptions(
        "sample", match_full_file_name=False, match_case=False, db=db_session
    )
    # Expect all three records to match when using lower-case search.
    assert len(results_partial) == 3

    # Test full file name match (case-insensitive).
    results_full = db_operations.db_search_transcriptions(
        "Sample1.mp3", match_full_file_name=True, match_case=False, db=db_session
    )
    assert len(results_full) == 1
    assert results_full[0].original_audio_filename == "Sample1.mp3"

    # Test full file name match with match_case=True (exact match).
    results_case_exact = db_operations.db_search_transcriptions(
        "sample1.mp3", match_full_file_name=True, match_case=True, db=db_session
    )
    # "Sample1.mp3" was saved so the exact (case-sensitive) match for "sample1.mp3" should return no records.
    assert len(results_case_exact) == 0
