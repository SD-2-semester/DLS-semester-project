from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)
from redis.asyncio import Redis

from chat_service.services.ws.ws import RedisPubSubManager, WebSocketManager
from chat_service.utils import dtos
from chat_service.web.lifetime import setup_redis

router = APIRouter()


def get_ws_manager(redis: Redis) -> WebSocketManager:  # type: ignore
    """Get WebSocket manager."""
    return WebSocketManager(pubsub_client=RedisPubSubManager(redis))


@router.websocket("/chats/{chat_id}/users/{user_id}")
async def ws_chat_connect(
    chat_id: UUID,
    user_id: UUID,
    websocket: WebSocket,
    background_tasks: BackgroundTasks,
) -> None:
    """Connect to chat websocket."""

    app = FastAPI()

    # await setup_db(app)
    # session = await get_db_session_ws(app)
    # r_daos = AllReadDAOs(session)
    # await get_chat_if_participant_ws(chat_id, user_id, r_daos)

    setup_redis(app)
    ws_manager = get_ws_manager(app.state.redis)

    s_room_id = str(chat_id)

    await ws_manager.connect_user(s_room_id, websocket, background_tasks)

    try:
        while True:

            data = await websocket.receive_text()
            await ws_manager.broadcast(
                s_room_id, dtos.ChatPublishDTO(message=data, chat_id=chat_id)
            )
            await websocket.send_text(data)
    except WebSocketDisconnect:
        await ws_manager.remove_user(s_room_id, websocket)


@router.websocket("/servers/{server_id}/users/{user_id}")
async def ws_server_connect(
    # server: GetServerIfMember,
    server_id: UUID,
    websocket: WebSocket,
    background_tasks: BackgroundTasks,
) -> None:
    """Connect to server websocket."""

    app = FastAPI()
    setup_redis(app)
    ws_manager = get_ws_manager(app.state.redis)

    s_room_id = str(server_id)

    await ws_manager.connect_user(s_room_id, websocket, background_tasks)

    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(
                s_room_id, dtos.ServerPublishDTO(message=data, server_id=server_id)
            )
            await websocket.send_text(data)
    except WebSocketDisconnect:
        await ws_manager.remove_user(s_room_id, websocket)
