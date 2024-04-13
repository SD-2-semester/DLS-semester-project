import uuid

from pydantic import BaseModel, ConfigDict, Field


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
