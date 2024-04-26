import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, computed_field


class BaseOrmModel(BaseModel):
    """BaseOrmModel."""

    model_config = ConfigDict(from_attributes=True)


class CreatedResponse(BaseModel):
    """Response model for created objects."""

    id: uuid.UUID = Field(..., description="ID of the created object.")


class DefaultCreatedResponse(BaseModel):
    """Default response model for created objects."""

    data: CreatedResponse
    success: bool = True
    message: str | None = "Object was created!"


class ComputedCreatedAt(BaseModel):
    """ComputedCreatedAt."""

    @computed_field  # type: ignore
    @property
    def created_at(self) -> datetime:
        """Get current datetime."""
        return datetime.now(timezone.utc)
