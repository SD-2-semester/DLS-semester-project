from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from chat_service.utils import dtos


class ServerMemberDTO(dtos.BaseOrmModel):
    """ServerMemberDTO."""

    id: UUID
    server_id: UUID
    user_id: UUID
    created_at: datetime


class ServerMemberInputDTO(BaseModel):
    """ServerMemberInputDTO."""

    server_id: UUID
    user_id: UUID


class ServerMemberRequestDTO(BaseModel):
    """ServerMemberRequestDTO."""

    user_id: UUID
