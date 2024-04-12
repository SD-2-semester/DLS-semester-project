from typing import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from chat_service.db.meta import meta
from chat_service.services.rabbit.lifetime import init_rabbit, shutdown_rabbit
from chat_service.settings import EnvLevel, settings


async def _setup_db_ro(app: FastAPI) -> None:  # pragma: no cover
    """Setup read only database."""

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


async def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """Setup database."""
    engine = create_async_engine(
        str(settings.pg.url),
        echo=settings.pg.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

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
    async def _startup() -> None:
        app.middleware_stack = None
        await _setup_db_ro(app)
        await _setup_db(app)

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
    async def _shutdown() -> None:
        await app.state.db_engine_ro.dispose()
        await app.state.db_engine.dispose()

        await shutdown_rabbit(app)

    return _shutdown
