from uuid import UUID

from pydantic import field_validator

from chat_service.utils import dtos

MAX_MESSAGE_LENGTH = 30


class _BaseNotificationDTO(dtos.ComputedCreatedAt):
    """Base model for publishing messages."""

    message: str
    sender_username: str = "System"

    @field_validator("message")
    @classmethod
    def trim_message(cls, msg: str) -> str:
        """Trim message to max length."""
        return (
            f"{msg[:MAX_MESSAGE_LENGTH - 3]}..."
            if len(msg) > MAX_MESSAGE_LENGTH
            else msg
        )


class RMQChatNotificationDTO(_BaseNotificationDTO):
    """DTO for publishing chat message in RabbitMQ."""

    chat_id: UUID
    user_id_1: UUID
    user_id_2: UUID


class RMQServerNotificationDTO(_BaseNotificationDTO):
    """DTO for publishing server message in RabbitMQ."""

    server_id: UUID
    user_id: UUID
