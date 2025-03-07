# import contextlib
# import os
# import shutil
# import tempfile

# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import StaticPool, create_engine
# from sqlalchemy.orm import sessionmaker

# # Patch the transcribe_audio_task in the websocket module.
# # import backend.routes.websocket as websocket_module
# from database import Base, Transcription, get_db
# from main import app

# # Monkey patch the background transcription task for file upload endpoint.
# # This dummy function will be used in place of the actual asynchronous task.
# # async def dummy_transcribe_audio_task(
# #     batch_uuid: str, file_paths: list[str], original_audio_names: list[str]
# # ):
# #     # Do nothing, or optionally simulate saving a dummy transcription record.
# #     return


# # websocket_module.transcribe_audio_task = dummy_transcribe_audio_task

# # Set the environment variable for the in-memory database
# os.environ["DATABASE_URL"] = "sqlite:///:memory:"


# @pytest.fixture(scope="module")
# def test_audio_storage_dir():
#     """
#     Create a temporary directory for audio uploads and override the AUDIO_STORAGE_PATH in main.
#     """
#     tmp_dir = tempfile.mkdtemp()
#     # Override the global AUDIO_STORAGE_PATH variable in main.py.
#     app.AUDIO_STORAGE_PATH = tmp_dir
#     yield tmp_dir
#     # Cleanup: remove the temporary directory and its files after tests.
#     shutil.rmtree(tmp_dir)


# @pytest.fixture(scope="module")
# def test_db():
#     """Create a temporary in-memory SQLite database for testing."""
#     engine = create_engine(
#         os.getenv("DATABASE_URL"),
#         connect_args={"check_same_thread": False},
#         poolclass=StaticPool,
#     )
#     testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#     def override_get_db():
#         try:
#             db = testing_session_local()
#             yield db
#         finally:
#             db.close()


#     app.dependency_overrides[get_db] = override_get_db

#     Base.metadata.create_all(bind=engine)

#     yield testing_session_local  # This will be the session used in tests

#     # Cleanup: drop the database after tests
#     Base.metadata.drop_all(bind=engine)


# @pytest.fixture
# def client(test_db, test_audio_storage_dir):
#     """
#     Create a TestClient instance with the in-memory database initialized.
#     Also, clear the Transcription table before and after each test.
#     """
#     with test_db() as db:
#         db.query(Transcription).delete()
#         db.commit()

#     client = TestClient(app)
#     yield client

#     # Teardown: remove any files that were uploaded during tests.
#     if os.path.isdir(test_audio_storage_dir):
#         for filename in os.listdir(test_audio_storage_dir):
#             file_path = os.path.join(test_audio_storage_dir, filename)
#             with contextlib.suppress(Exception):
#                 os.remove(file_path)
#     with test_db() as db:
#         db.query(Transcription).delete()
#         db.commit()


# def insert_transcriptions(db, entries):
#     """
#     Helper function to insert a list of transcription records into the database.
#     Each entry is a dict that should contain 'original_audio_filename' and optionally
#     'audio_filepath' and 'text'.
#     """
#     for entry in entries:
#         transcription = Transcription(
#             audio_filepath=entry.get(
#                 "audio_filepath", entry["original_audio_filename"]
#             ),
#             original_audio_filename=entry["original_audio_filename"],
#             text=entry.get("text", "dummy transcription"),
#         )
#         db.add(transcription)
#     db.commit()


# def test_health_check(client):
#     response = client.get("/api/health")
#     assert response.status_code == 200
#     assert response.json() == {"status": "OK"}


# def test_get_transcriptions(client, test_db):
#     # Insert dummy transcriptions into the database.
#     entries = [
#         {
#             "original_audio_filename": "test_audio1.mp3",
#             "audio_filepath": "test_audio1.mp3",
#             "text": "dummy transcription text 1",
#         },
#         {
#             "original_audio_filename": "Test_Audio2.MP3",
#             "audio_filepath": "Test_Audio2.MP3",
#             "text": "dummy transcription text 2",
#         },
#     ]
#     with test_db() as db:
#         insert_transcriptions(db, entries)

#     response = client.get("/api/transcriptions")
#     assert response.status_code == 200
#     data = response.json()
#     assert isinstance(data, list)
#     assert len(data) == 2


# def test_search_transcriptions_case_insensitive_and_sensitive(client):
#     # Populate the database with test records.
#     entries = [
#         {"original_audio_filename": "Sample1.mp3", "text": "text 1"},
#         {"original_audio_filename": "sample2.mp3", "text": "text 2"},
#         {"original_audio_filename": "another_sample.MP3", "text": "text 3"},
#         {"original_audio_filename": "sample_extra.mp3", "text": "text 4"},
#     ]
#     insert_transcriptions(entries)

#     # Default search: case-insensitive partial matching.
#     response = client.get("/api/search", params={"file_name": "sample"})
#     assert response.status_code == 200
#     data = response.json()
#     # Expect at least "Sample1.mp3", "sample2.mp3", "sample_extra.mp3" to match.
#     found_files = {d["original_audio_filename"] for d in data}
#     for expected in ("Sample1.mp3", "sample2.mp3", "sample_extra.mp3"):
#         assert expected in found_files

#     # Test full file name matching (case-insensitive).
#     response = client.get(
#         "/api/search", params={"file_name": "Sample1.mp3", "match_full_file_name": True}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 1
#     assert data[0]["original_audio_filename"] == "Sample1.mp3"

#     # Test full file name matching with match_case=True (should be exact).
#     response = client.get(
#         "/api/search",
#         params={
#             "file_name": "sample1.mp3",
#             "match_full_file_name": True,
#             "match_case": True,
#         },
#     )
#     assert response.status_code == 200
#     data = response.json()
#     # Since "Sample1.mp3" (with capital S) is stored, this should return no match.
#     assert len(data) == 0

#     # Test partial search with case sensitivity.
#     response = client.get(
#         "/api/search", params={"file_name": "Sample", "match_case": True}
#     )
#     assert response.status_code == 200
#     data = response.json()
#     # Only "Sample1.mp3" should match as it has an uppercase 'S'.
#     found_files = {d["original_audio_filename"] for d in data}
#     assert "Sample1.mp3" in found_files
#     assert "sample2.mp3" not in found_files


# def test_upload_file(client, test_audio_storage_dir):
#     # Create a dummy audio file in memory with an allowed extension (mp3).
#     dummy_file_content = b"dummy audio content"
#     files = {"files": ("dummy.mp3", BytesIO(dummy_file_content), "audio/mp3")}

#     response = client.post("/api/transcribe", files=files)
#     # We expect a 202 Accepted response.
#     assert response.status_code == 202
#     data = response.json()
#     assert "batch_uuid" in data

#     # Check that the file was written into the test audio storage directory.
#     uploaded_files = os.listdir(test_audio_storage_dir)
#     assert any("dummy.mp3" in filename for filename in uploaded_files)
