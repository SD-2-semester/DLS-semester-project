from uuid import UUID

from fastapi import (
    APIRouter,
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
)

from chat_service.services.ws.ws import ws_manager
from chat_service.utils import dtos
from chat_service.web.lifetime import setup_redis

router = APIRouter()


@router.websocket("/chats/{chat_id}/users/{user_id}")
async def ws_chat_connect(
    chat_id: UUID,
    user_id: UUID,
    websocket: WebSocket,
) -> None:
    """Connect to chat websocket."""

    app = FastAPI()

    # await setup_db(app)
    # session = await get_db_session_ws(app)
    # r_daos = AllReadDAOs(session)
    # await get_chat_if_participant_ws(chat_id, user_id, r_daos)

    setup_redis(app)
    ws_manager.set_pubsub_client(app.state.redis)

    s_room_id = str(chat_id)  #

    await ws_manager.connect_user(s_room_id, websocket)

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
) -> None:
    """Connect to server websocket."""

    app = FastAPI()
    setup_redis(app)
    ws_manager.set_pubsub_client(app.state.redis)

    s_room_id = str(server_id)

    await ws_manager.connect_user(s_room_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(
                s_room_id, dtos.ServerPublishDTO(message=data, server_id=server_id)
            )
    except WebSocketDisconnect:
        await ws_manager.remove_user(s_room_id, websocket)
