from fastapi import APIRouter

from chat_service.settings import settings

router = APIRouter()


@router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """


@router.get("/settings")
def get_settings(setting: str) -> str:
    """Returns the current settings of the project."""
    return repr(getattr(settings, setting))
