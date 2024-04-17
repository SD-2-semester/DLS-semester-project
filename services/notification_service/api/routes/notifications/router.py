from fastapi import APIRouter, WebSocket
from api.routes.notifications.ws_connection_manager import ws_manager

router = APIRouter()


@router.get("/hello")
async def hello():
    return "hello"


@router.websocket("/notification/{user_id}")
async def sub_notifications(websocket: WebSocket, user_id: str) -> None:
    print("hello before")
    await ws_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            print("yoo", data)
            # Send message only to client with user id
            await ws_manager.broadcast(data, user_id)
    except Exception:
        await ws_manager.disconnect(websocket, user_id)
