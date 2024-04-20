from datetime import datetime, timezone
from uuid import UUID

from pydantic import computed_field
from redis.asyncio import Redis

from chat_service.settings import settings
from chat_service.utils import dtos


class _BasePublishDTO(dtos.BaseOrmModel):
    """Base model for publishing messages."""

    message: str

    @computed_field
    @property
    def created_at(self) -> datetime:
        return datetime.now(timezone.utc)


class ChatPublishDTO(_BasePublishDTO):
    """Message to publish to chat participant."""

    chat_id: UUID


class ServerPublishDTO(_BasePublishDTO):
    """Message to publish to server members."""

    server_id: UUID


MessageType = ChatPublishDTO | ServerPublishDTO


def get_redis() -> Redis:
    """Get redis connection."""

    return Redis.from_url(str(settings.redis.url))
