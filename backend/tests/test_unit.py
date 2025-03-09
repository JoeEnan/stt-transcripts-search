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
    """
    Create the SQLAlchemy engine for an in-memory SQLite database.
    """
    engine = create_engine(
        os.getenv("DATABASE_URL"),
        connect_args={"check_same_thread": False},
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def setup_database(test_engine):
    """
    Setup and teardown the database schema for the test module.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session(test_engine):
    """
    Create a new SQLAlchemy session for each test and ensure a clean database state.
    """
    test_session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = test_session()
    session.query(Transcription).delete()
    session.commit()
    yield session
    session.close()


# -------------------------------
# Dummy Test Helpers
# -------------------------------
def dummy_model():
    """
    Create a dummy transcription model for testing purposes.
    """

    class Dummy:
        def transcribe(self, file_path: str):  # noqa: ARG002 Keep the signature for compatibility with the real model.
            return {"text": "dummy transcribed text"}

    return Dummy()


class DummyWebSocket:
    """
    A dummy websocket for collecting sent messages in tests.
    """

    def __init__(self):
        self.sent_messages = []
        self.closed = False

    async def send_json(self, message):
        self.sent_messages.append(message)

    async def close(self):
        self.closed = True


# -------------------------------
# Tests for transcriber.py
# -------------------------------
def test_transcribe_audio(monkeypatch):
    """
    Verify that transcriber.transcribe_audio returns the expected transcription text
    when the underlying transcription model is mocked.
    """
    # Monkey-patch get_model to return a dummy model.
    monkeypatch.setattr("utils.transcriber.get_model", lambda: dummy_model())
    from utils import transcriber

    result = transcriber.transcribe_audio("dummy_audio_path.mp3")
    assert result == "dummy transcribed text"


@pytest.mark.asyncio
async def test_process_transcription_batch(db_session, monkeypatch):
    """
    Test the asynchronous batch transcription process by verifying that:
        - The dummy transcription model returns a preset transcription.
        - The transcriptions are correctly saved to the database.
        - The corresponding websocket receives the right messages.
    """
    clear_websockets()

    # Monkey-patch get_model to return a dummy model that returns a specific string.
    monkeypatch.setattr("utils.transcriber.get_model", lambda: dummy_model())

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
    Confirm that a transcription record saved using db_operations can be retrieved correctly.
    """
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
    Test the db_search_transcriptions function from the db_operations module with various search criteria.

    This test verifies that:
        - A partial search (case-insensitive) returns all records containing the search term.
        - A full file name match (case-insensitive) with an exact file name returns records regardless of case.
        - A partial search with case sensitivity returns only the records where the search term appears with exact case.
        - A full file name match with case sensitivity returns exactly one record for an exact match.
    """
    # Insert multiple records into the database.
    db_operations.db_save_transcription(
        "audio1.mp3", "Sample1.mp3", "text 1", db=db_session
    )
    db_operations.db_save_transcription(
        "audio1.mp3", "Sample11.mp3", "text 1", db=db_session
    )
    db_operations.db_save_transcription(
        "audio1.mp3", "sample1.mp3", "text 2", db=db_session
    )
    db_operations.db_save_transcription(
        "audio2.mp3", "sample2.mp3", "text 3", db=db_session
    )
    db_operations.db_save_transcription(
        "audio3.mp3", "another_sample.MP3", "text 4", db=db_session
    )

    # Test partial search (case-insensitive).
    # Searching for "sample" should return all 5 records because "sample" appears (ignoring case)
    # in each original_audio_filename.
    results_partial = db_operations.db_search_transcriptions(
        "sample", match_full_file_name=False, match_case=False, db=db_session
    )
    assert len(results_partial) == 5

    # Test full file name match (case-insensitive):
    # Using "Sample1.mp3" should match both "Sample1.mp3" and "sample1.mp3" when performing a full
    # file name match without considering case.
    results_full_insensitive = db_operations.db_search_transcriptions(
        "Sample1.mp3", match_full_file_name=True, match_case=False, db=db_session
    )
    assert len(results_full_insensitive) == 2, (
        f"Expected 2 records for case-insensitive full-match; got: {results_full_insensitive}"
    )
    # Verify that the matched filenames are exactly "Sample1.mp3" and "sample1.mp3".
    filenames = {record.original_audio_filename for record in results_full_insensitive}
    assert filenames == {"Sample1.mp3", "sample1.mp3"}

    # Test partial search with case sensitivity:
    # Using "Sample1" should return only those filenames where the substring "Sample1" appears with the exact case.
    # In this case, it should match "Sample1.mp3" and "Sample11.mp3".
    results_partial_sensitive = db_operations.db_search_transcriptions(
        "Sample1", match_full_file_name=False, match_case=True, db=db_session
    )
    assert len(results_partial_sensitive) == 2, (
        f"Expected 2 records for case-sensitive partial search; got: {results_partial_sensitive}"
    )
    # Check that the returned filenames are "Sample1.mp3" and "Sample11.mp3".
    filenames = {record.original_audio_filename for record in results_partial_sensitive}
    assert filenames == {"Sample1.mp3", "Sample11.mp3"}

    # Test full file name match with case sensitivity (exact match):
    # Using "Sample1.mp3" should return only the record with an exact matching original_audio_filename.
    results_full_sensitive = db_operations.db_search_transcriptions(
        "Sample1.mp3", match_full_file_name=True, match_case=True, db=db_session
    )
    assert len(results_full_sensitive) == 1, (
        f"Expected 1 record for case-sensitive full-match; got: {results_full_sensitive}"
    )
    assert results_full_sensitive[0].original_audio_filename == "Sample1.mp3"
