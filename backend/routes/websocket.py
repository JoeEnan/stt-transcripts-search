import os

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from utils.transcriber import save_transcription, transcribe_audio

router = APIRouter(prefix="/ws", tags=["websocket"])

connected_websockets = set()


@router.websocket("/transcript_ready")
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
