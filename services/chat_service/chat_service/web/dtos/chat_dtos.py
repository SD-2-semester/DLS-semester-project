from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

from chat_service.utils import dtos


class ChatDTO(dtos.BaseOrmModel):
    """ChatDTO."""

    id: UUID
    user_id_1: UUID
    user_id_2: UUID
    created_at: datetime


class ChatInputDTO(BaseModel):
    """ChatInputDTO."""

    user_id_1: UUID
    user_id_2: UUID

    @model_validator(mode="after")
    def _ensure_not_eq(self: "ChatInputDTO") -> "ChatInputDTO":
        """Validate that the user ID's are not the same."""

        if self.user_id_1 == self.user_id_2:
            raise ValueError("User ID's cannot be the same.")

        return self

    @model_validator(mode="after")
    def _ensure_ordered(self: "ChatInputDTO") -> "ChatInputDTO":
        """Make sure that the user ID's are in the correct order."""

        if self.user_id_1 > self.user_id_2:
            self.user_id_1, self.user_id_2 = self.user_id_2, self.user_id_1

        return self
