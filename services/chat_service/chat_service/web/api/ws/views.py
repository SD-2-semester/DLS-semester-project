from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect

from chat_service.services.ws.ws import ws_manager
from chat_service.utils import dtos
from chat_service.web.api.chat.dependencies import GetChatIfParticipant
from chat_service.web.api.server.dependencies import GetServerIfMember

router = APIRouter()


@router.websocket("/chats/{chat_id}/users/{user_id}")
async def ws_chat_connect(
    chat: GetChatIfParticipant,
    websocket: WebSocket,
    background_tasks: BackgroundTasks,
) -> None:
    """..."""

    s_room_id = str(chat.id)

    await ws_manager.connect_user(s_room_id, websocket, background_tasks)

    try:
        while True:

            data = await websocket.receive_text()
            await ws_manager.broadcast(
                s_room_id, dtos.ChatPublishDTO(message=data, chat_id=chat.id)
            )
    except WebSocketDisconnect:
        await ws_manager.remove_user(s_room_id, websocket)


@router.websocket("/servers/{chat_id}/users/{user_id}")
async def ws_server_connect(
    server: GetServerIfMember,
    websocket: WebSocket,
    background_tasks: BackgroundTasks,
) -> None:
    """..."""

    s_room_id = str(server.id)

    await ws_manager.connect_user(s_room_id, websocket, background_tasks)

    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.broadcast(
                s_room_id, dtos.ServerPublishDTO(message=data, server_id=server.id)
            )
    except WebSocketDisconnect:
        await ws_manager.remove_user(s_room_id, websocket)
