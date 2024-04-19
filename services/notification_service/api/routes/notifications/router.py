import json

from api.routes.notifications.ws_connection_manager import ws_manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/notification/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str) -> None:
    """Connect user by user_id and create a websocket session."""

    # Connect the user
    await ws_manager.connect_user(user_id, websocket)

    try:
        while True:
            # Receive messages
            data = await websocket.receive_text()

            # could be a dto
            message = {"user_id": user_id, "message": data}

            # Broadcast user message
            await ws_manager.send_notification(user_id, json.dumps(message))

    except WebSocketDisconnect:
        await ws_manager.disconnect_user(user_id, websocket)
