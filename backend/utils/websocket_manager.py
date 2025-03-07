connected_websockets = {}


def add_websocket(batch_uuid: str, websocket) -> None:
    """Add a WebSocket connection to the manager."""
    if batch_uuid not in connected_websockets:
        connected_websockets[batch_uuid] = set()
    connected_websockets[batch_uuid].add(websocket)


def remove_websocket(batch_uuid: str, websocket) -> None:
    """Remove a WebSocket connection from the manager."""
    if batch_uuid in connected_websockets:
        connected_websockets[batch_uuid].remove(websocket)
        if not connected_websockets[batch_uuid]:
            del connected_websockets[batch_uuid]


def get_websockets(batch_uuid: str):
    """Get the list of WebSockets for a given batch UUID."""
    return connected_websockets.get(batch_uuid, set())


def clear_websockets() -> None:
    """Clear all WebSocket connections from the manager."""
    connected_websockets.clear()
