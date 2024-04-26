from typing import Annotated, Generic, TypeVar

from fastapi import Depends
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """DTO for offset pagination."""

    offset: int = Field(0, ge=0)
    limit: int = Field(20, le=20, ge=1)


DataT = TypeVar("DataT", bound=BaseModel)


class OffsetResults(BaseModel, Generic[DataT]):
    """DTO for offset paginated response."""

    data: list[DataT]


Pagination = Annotated[PaginationParams, Depends(PaginationParams)]
