import pytest
from fastapi.testclient import TestClient

from database import init_db
from main import app


@pytest.fixture
def client():
    # Ensure that database is initialized.
    init_db()
    return TestClient(app)


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


# def test_transcription(client):
#     audio_file_path = "tests/backend/test_audio/Sample 1.mp3"
#     with open(audio_file_path, "rb") as audio_file:
#         files = {"file": (audio_file)}
#         response = client.post("/api/transcribe", files=files)

#     assert response.status_code == 200
#     assert "text" in response.json()  # Check if a transcription text is returned


# def test_get_transcriptions(client):
#     response = client.get("/api/transcriptions")
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)  # Ensure response is a list


# def test_search_transcriptions():
#     response = client.get("/api/search", params={"file_name": "Sample 1.mp3"})
#     assert response.status_code == 200
#     assert isinstance(response.json(), list)  # Ensure response is a list
#     # Optionally check for known values in the response
