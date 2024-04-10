from fastapi.routing import APIRouter
from chat_service.web.api import echo
from chat_service.web.api import rabbit
from chat_service.web.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(rabbit.router, prefix="/rabbit", tags=["rabbit"])
