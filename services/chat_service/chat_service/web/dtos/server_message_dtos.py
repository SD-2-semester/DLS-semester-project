from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from chat_service.utils import dtos


class ServerMessageDTO(dtos.BaseOrmModel):
    """ServerMessageDTO."""

    id: UUID
    server_id: UUID
    message: str
    created_at: datetime


class ServerMessageInputDTO(BaseModel):
    """ServerMessageInputDTO."""

    server_id: UUID
    message: str


class ServerMessageRequestDTO(BaseModel):
    """ServerMessageRequestDTO."""

    message: str


class ServerElasticDTO(BaseModel):
    """ServerElasticDTO."""

    server_id: UUID
    message: str
