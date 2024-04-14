from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from chat_service.utils import dtos


class ServerDTO(dtos.BaseOrmModel):
    """ServerDTO."""

    id: UUID
    title: str
    created_at: datetime


class ServerInputDTO(BaseModel):
    """ServerInputDTO."""

    title: str
    owner_id: UUID
