from typing import Awaitable, Callable

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from chat_service.db.meta import meta
from chat_service.services.rabbit.lifetime import init_rabbit, shutdown_rabbit
from chat_service.settings import settings


async def _setup_db_ro(app: FastAPI) -> None:  # pragma: no cover
    """Setup read only database."""
    engine = create_async_engine(
        str(settings.pg_ro.url),
        echo=settings.pg_ro.echo,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    app.state.db_engine_ro = engine
    app.state.db_session_ro_factory = session_factory

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

    async with engine.begin() as connection:
        await connection.run_sync(meta.create_all)

    # query = """
    #    GRANT SELECT ON ALL TABLES IN SCHEMA public TO repl_user;
    # """

    # await connection.execute(text(query))

    # query = """
    #    ALTER DEFAULT PRIVILEGES IN SCHEMA public
    #    GRANT SELECT ON TABLES TO repl_user;
    # """

    # await connection.execute(text(query))

    await engine.dispose()


def _setup_redis(app: FastAPI) -> None:
    """Setup Redis."""
    app.state.redis = Redis.from_url(
        str(settings.redis.url),
        auto_close_connection_pool=False,
    )


async def _setup_es(app: FastAPI) -> None:
    """Setup Elasticsearch."""
    es_client = AsyncElasticsearch(
        hosts=[{"host": settings.es.host, "port": 9200}],
        api_key=settings.es.api_key,
    )
    await es_client.info()
    app.state.es = es_client


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
        await _setup_db(app)
        await _setup_db_ro(app)

        _setup_redis(app)
        await _setup_es(app)

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
        # await app.state.redis_connection.disconnect()
        await app.state.es.close()

        await shutdown_rabbit(app)

    return _shutdown
