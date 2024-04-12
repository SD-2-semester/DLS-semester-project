import uuid

from pydantic import Field, BaseModel


class CreatedResponse(BaseModel):
    """Response model for created objects."""

    id: uuid.UUID = Field(..., description="ID of the created object.")


class DefaultCreatedResponse(BaseModel):
    """Default response model for created objects."""

    data: CreatedResponse
    success: bool = True
    message: str | None = "Object was created!"
