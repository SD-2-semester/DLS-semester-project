from chat_service.utils.daos import ReadDAOs
from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
async def test(daos: ReadDAOs) -> None:
    """."""
