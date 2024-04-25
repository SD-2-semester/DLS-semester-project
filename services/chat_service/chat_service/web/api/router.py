from fastapi.routing import APIRouter

from chat_service.web.api import (
    chat,
    chat_message,
    demo,
    echo,
    monitoring,
    server,
    server_member,
    server_message,
    ws,
)

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
api_router.include_router(server.router, prefix="/servers", tags=["servers"])
api_router.include_router(
    server_message.router, prefix="/server-messages", tags=["server-messages"]
)
api_router.include_router(
    server_member.router, prefix="/server-members", tags=["server-members"]
)
api_router.include_router(
    chat_message.router, prefix="/chat-messages", tags=["chat-messages"]
)
api_router.include_router(ws.router, prefix="/ws", tags=["ws"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
