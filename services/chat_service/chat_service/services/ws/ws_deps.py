from uuid import UUID

from chat_service.utils import dtos


class _BasePublishDTO(dtos.BaseOrmModel, dtos.ComputedCreatedAt):
    """Base model for publishing messages."""

    message: str


class ChatPublishDTO(_BasePublishDTO):
    """Message to publish to chat participant."""

    chat_id: UUID


class ServerPublishDTO(_BasePublishDTO):
    """Message to publish to server members."""

    server_id: UUID


MessageType = ChatPublishDTO | ServerPublishDTO
