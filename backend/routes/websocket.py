import os

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from utils.transcriber import save_transcription, transcribe_audio

router = APIRouter(prefix="/ws", tags=["websocket"])

connected_websockets = {}


@router.websocket("/transcript_ready/{batch_uuid}")
async def websocket_endpoint(websocket: WebSocket, batch_uuid: str):
    await websocket.accept()
    connected_websockets[batch_uuid] = connected_websockets.get(batch_uuid, set())
    connected_websockets[batch_uuid].add(websocket)
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
        connected_websockets[batch_uuid].remove(websocket)
        if not connected_websockets[batch_uuid]:
            del connected_websockets[batch_uuid]
        try:
            await websocket.close()
        except RuntimeError:
            print("WebSocket already closed.")


async def transcribe_audio_task(batch_uuid: str, file_paths: list[str]):
    # This will run asynchronously as needed by Whisper
    for file_path in file_paths:
        transcribed_text = transcribe_audio(file_path)
        save_transcription(file_path, os.path.basename(file_path), transcribed_text)
        # Notify relevant connected WebSocket clients that transcription is done
        for websocket in connected_websockets.get(batch_uuid, set()):
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
