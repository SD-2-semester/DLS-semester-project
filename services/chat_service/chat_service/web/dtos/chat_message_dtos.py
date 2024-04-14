from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from chat_service.utils import dtos


class ChatMessageDTO(dtos.BaseOrmModel):
    """ChatMessageDTO."""

    id: UUID
    chat_id: UUID
    message: str
    created_at: datetime


class ChatMessageInputDTO(BaseModel):
    """ChatMessageInputDTO."""

    chat_id: UUID
    message: str


class ChatMessageRequestDTO(BaseModel):
    """ChatMessageRequestDTO."""

    user_id: UUID
    message: str
