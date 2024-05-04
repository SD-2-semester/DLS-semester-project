from typing import Any, Generic, Type, TypeVar, get_args, get_origin
from uuid import UUID, uuid4

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

from chat_service import exceptions
from chat_service.core.pagination_dtos import OffsetResults, PaginationParams
from chat_service.db.models import Base

Model = TypeVar("Model", bound=Base)
InputDTO = TypeVar("InputDTO", bound=BaseModel)
OutputDTO = TypeVar("OutputDTO", bound=BaseModel)

LoadType = orm.interfaces.LoaderOption | orm.InstrumentedAttribute  # type: ignore
PaginationType = PaginationParams


class _Base(Generic[Model]):
    model: Type[Model]

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    @classmethod
    def __init_subclass__(cls) -> None:
        """Set `model` attribute for each subclass of `_Base`."""
        super().__init_subclass__()
        for base in cls.__orig_bases__:  # type: ignore[attr-defined]
            origin = get_origin(base)
            if origin is None or not issubclass(origin, _Base):
                continue
            model = get_args(base)[0]
            if not isinstance(model, TypeVar):
                cls.model = model
                return


class BaseDAORO(
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

    async def filter_one(
        self,
        loads: list[LoadType] | None = None,
        **filter_params: Any,
    ) -> Model | None:
        """Get a record by filters."""

        query = sa.select(self.model)

        for key, value in filter_params.items():
            if not hasattr(self.model, key):
                raise ValueError(
                    f"Model '{self.model.__name__}' does not have attr: '{key}'"
                )

            query = query.where(getattr(self.model, key) == value)

        query = query.limit(1)

        if loads:
            query = self._eager_load(query, loads)

        results = await self.session.execute(query)
        return results.scalar_one_or_none()

    async def get_offset_results(
        self,
        out_dto: Type[OutputDTO],
        pagination: PaginationType | None = None,
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


class BaseDAOWO(
    _Base[Model],
    Generic[Model, InputDTO],
):
    """Base class for interacting with the WRITE database."""

    async def create(self, input_dto: InputDTO, id: UUID | None = None) -> UUID:
        """Create a record."""

        if id is None:
            id = uuid4()

        base = self.model(id=id, **input_dto.model_dump())
        self.session.add(base)
        await self.session.flush()
        return id
