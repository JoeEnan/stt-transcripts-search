from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from log_config import logger
from utils.websocket_manager import add_websocket, remove_websocket

router = APIRouter(prefix="/ws", tags=["websocket"])

connected_websockets = {}


@router.websocket("/transcript_ready/{batch_uuid}")
async def websocket_endpoint(websocket: WebSocket, batch_uuid: str):
    await websocket.accept()
    add_websocket(batch_uuid, websocket)  # Add the new websocket connection
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json(
                {"status": "message_received", "message": message}
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
    finally:
        remove_websocket(batch_uuid, websocket)  # Remove the websocket on disconnect
        try:
            await websocket.close()
        except RuntimeError:
            logger.info("WebSocket already closed.")
