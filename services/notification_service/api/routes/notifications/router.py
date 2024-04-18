from fastapi import WebSocket, APIRouter
from api.routes.notifications.ws_connection_manager import ws_manager
from fastapi import WebSocket, WebSocketDisconnect
import json

router = APIRouter()


@router.websocket("/notification/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Connect user by user_id."""
    await ws_manager.connect_user(user_id, websocket)  # Connect the user
    message = {
        "user_id": user_id,
        "message": f"User {user_id} connected.",
    }
    await ws_manager.send_notification(
        user_id, json.dumps(message)
    )  # Send connection notification
    try:
        while True:
            data = await websocket.receive_text()  # Receive message from the user
            message = {"user_id": user_id, "message": data}
            await ws_manager.send_notification(
                user_id, json.dumps(message)
            )  # Broadcast user message

    except WebSocketDisconnect:
        await ws_manager.disconnect_user(user_id, websocket)  # Disconnect the user
        message = {
            "user_id": user_id,
            "message": f"User {user_id} disconnected.",
        }
        await ws_manager.send_notification(
            user_id, json.dumps(message)
        )  # Notify about user disconnection
