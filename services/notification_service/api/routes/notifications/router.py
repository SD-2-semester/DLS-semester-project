from fastapi import WebSocket, APIRouter
from api.routes.notifications.ws_connection_manager import ws_manager
from fastapi import WebSocket, WebSocketDisconnect
import json

router = APIRouter()


@router.websocket("/notification/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
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


# @router.websocket("/notification/{room_id}/{user_id}")
# async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: int):
#     await ws_manager.add_user_to_room(room_id, websocket)
#     message = {
#         "user_id": user_id,
#         "room_id": room_id,
#         "message": f"User {user_id} connected to room - {room_id}",
#     }
#     await ws_manager.broadcast_to_room(room_id, json.dumps(message))
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = {"user_id": user_id, "room_id": room_id, "message": data}
#             await ws_manager.broadcast_to_room(room_id, json.dumps(message))

#     except WebSocketDisconnect:
#         await ws_manager.remove_user_from_room(room_id, websocket)

#         message = {
#             "user_id": user_id,
#             "room_id": room_id,
#             "message": f"User {user_id} disconnected from room - {room_id}",
#         }
#         await ws_manager.broadcast_to_room(room_id, json.dumps(message))
