from typing import Awaitable, Callable

from fastapi import FastAPI
from chat_service.settings import settings, EnvLevel
from chat_service.services.rabbit.lifetime import (
    init_rabbit,
    shutdown_rabbit,
)
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from chat_service.db.meta import meta


async def _setup_db_ro(app: FastAPI) -> None:  # pragma: no cover
    """Setup read database."""

    engine = create_async_engine(
        str(settings.pg_ro.url),
        echo=settings.pg_ro.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine_ro = engine
    app.state.db_session_ro_factory = session_factory

    if settings.env_level == EnvLevel.local:
        async with engine.begin() as connection:
            await connection.run_sync(meta.create_all)
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))

    await engine.dispose()


async def _setup_db_wo(app: FastAPI) -> None:  # pragma: no cover
    """Setup write database."""
    engine = create_async_engine(
        str(settings.pg_wo.url),
        echo=settings.pg_wo.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine_wo = engine
    app.state.db_session_wo_factory = session_factory

    if settings.env_level == EnvLevel.local:
        async with engine.begin() as connection:
            await connection.run_sync(meta.create_all)
            await connection.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))

    await engine.dispose()


def register_startup_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        await _setup_db_ro(app)
        await _setup_db_wo(app)

        init_rabbit(app)
        app.middleware_stack = app.build_middleware_stack()

    return _startup


def register_shutdown_event(
    app: FastAPI,
) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine_ro.dispose()
        await app.state.db_engine_wo.dispose()

        await shutdown_rabbit(app)

    return _shutdown
