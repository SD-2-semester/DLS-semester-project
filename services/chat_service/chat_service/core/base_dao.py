# kun modellen
from uuid import UUID, uuid4
from chat_service import exceptions
from chat_service.core.pagination_dtos import OffsetResults, PaginationParams
from chat_service.db.models import Base
from pydantic import BaseModel
from chat_service.db.dependencies import get_db_session_ro
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TypeVar, Type, Generic
import sqlalchemy as sa
from sqlalchemy import orm

Model = TypeVar("Model", bound=Base)
InputDTO = TypeVar("InputDTO", bound=BaseModel)
OutputDTO = TypeVar("OutputDTO", bound=BaseModel)

LoadType = orm.interfaces.LoaderOption | orm.InstrumentedAttribute
PaginationType = PaginationParams


class _Base(Generic[Model]):
    model: Type[Model]

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session_ro),
    ):
        self.session = session


class BaseDAORO(
    Generic[Model],
    _Base[Model],
):
    """Base class for interacting with the READ database."""

    async def get_by_id_or_error(
        self,
        id: UUID,
        loads: list[LoadType] | None = None,
        exception: Exception | None = None,
    ) -> Model:
        """Get a record by ID."""

        query = sa.select(self.model).where(self.model.id == id)

        if loads:
            query = self._eager_load(query, loads)

        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()

        if obj is None:
            name = self.model.__name__
            exception = exception or exceptions.Http404(f"{name} not found.")
            raise exception

        return obj

    async def get_offset_results(
        self,
        out_dto: Type[OutputDTO],
        pagination: PaginationType,
        query: sa.sql.Select[tuple[Model]] | None = None,
    ) -> OffsetResults[OutputDTO]:
        """Get offset paginated records."""

        if query is None:
            query = sa.select(self.model)

        query = query.offset(pagination.offset).limit(pagination.limit)
        results = await self.session.execute(query)

        return OffsetResults(
            data=[out_dto.model_validate(row) for row in results.scalars()],
        )

    @staticmethod
    def _eager_load(
        query: sa.sql.Select[tuple[Model]],
        loads: list[LoadType],
    ) -> sa.sql.Select[tuple[Model]]:
        """Eager load items to query."""

        for load in loads:
            if isinstance(load, orm.InstrumentedAttribute):
                query = query.options(orm.joinedload(load))
            else:
                query = query.options(load)

        return query


# input model
class BaseDAOWO(_Base):
    """Base class for interacting with the WRITE database."""

    async def create(self, input_dto: InputDTO, id: UUID | None = None) -> UUID:
        """Create a record."""

        if id is None:
            id = uuid4()

        base = self.model(id=id, **input_dto.model_dump())
        self.session.add(base)
        await self.session.flush()
        return id
