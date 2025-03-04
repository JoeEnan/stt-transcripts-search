import asyncio
import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from utils.transcriber import save_transcription, transcribe_audio

router = APIRouter(prefix="/api", tags=["transcriptions"])

AUDIO_STORAGE_PATH = "backend/audio_storage"
os.makedirs(AUDIO_STORAGE_PATH, exist_ok=True)

connected_websockets = set()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {"status": "message_received", "message": message}
            )
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
    finally:
        connected_websockets.remove(websocket)
        try:
            await websocket.close()
        except RuntimeError:
            print("WebSocket already closed.")


async def transcribe_audio_task(file_path: str, original_audio_filename: str):
    # This will run asynchronously as needed by Whisper
    transcribed_text = transcribe_audio(file_path)
    save_transcription(file_path, original_audio_filename, transcribed_text)
    # Notify all connected WebSocket clients that transcription is done
    for websocket in connected_websockets:
        try:
            await websocket.send_json(
                {
                    "status": "completed",
                    "file": os.path.basename(file_path),
                    "text": transcribed_text,
                }
            )
        except Exception as e:
            print(f"Failed to send message over WebSocket: {e}")


@router.post("/transcribe")
async def transcribe(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
) -> JSONResponse:
    if not file.filename.endswith((".wav", ".mp3", ".m4a")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    audio_path = os.path.join(AUDIO_STORAGE_PATH, unique_filename)
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Start transcription task
    background_tasks.add_task(
        run_in_threadpool,
        lambda: asyncio.run(transcribe_audio_task(audio_path, file.filename)),
    )

    return JSONResponse(
        content={"message": "File uploaded, transcription started."}, status_code=202
    )


# @router.get("/transcriptions")
# async def get_transcriptions(db: Session = Depends(get_db)):
#     transcriptions = db.query(Transcription).all()
#     return transcriptions


# @router.get("/search")
# async def search(file_name: str, db: Session = Depends(get_db)):
#     results = search_transcriptions(db, file_name)
#     return results
