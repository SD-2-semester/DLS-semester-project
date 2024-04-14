from fastapi.routing import APIRouter

from chat_service.web.api import chat, echo, monitoring, rabbit, server, server_message

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
api_router.include_router(server.router, prefix="/servers", tags=["servers"])
api_router.include_router(
    server_message.router, prefix="/server-messages", tags=["server-messages"]
)
