from fastapi import APIRouter
from api.routes.notifications.router import (
    router as notification_router,
)

router = APIRouter()

router.include_router(notification_router, prefix="/ws", tags=["websocket"])
