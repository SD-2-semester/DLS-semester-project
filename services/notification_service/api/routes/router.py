from api.routes.notifications.router import router as notification_router
from fastapi import APIRouter

router = APIRouter()

router.include_router(notification_router, prefix="/ws", tags=["websocket"])
