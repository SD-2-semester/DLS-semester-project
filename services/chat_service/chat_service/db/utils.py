from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from chat_service.settings import settings


async def create_database(db_name: str) -> None:
    """Create a database."""
    db_url = make_url(str(settings.pg.url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{db_name}'",
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database(db_name)

    async with engine.connect() as conn:
        await conn.execute(
            text(
                f'CREATE DATABASE "{db_name}" ENCODING "utf8" TEMPLATE template1',
            ),
        )


async def drop_database(db_name: str) -> None:
    """Drop current database."""
    db_url = make_url(str(settings.pg.url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            + "FROM pg_stat_activity "
            + f"WHERE pg_stat_activity.datname = '{db_name}' "
            + "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(
            text(f'DROP DATABASE IF EXISTS "{db_name}"'),
        )


async def create_extensions(db_url: str) -> None:
    """Create extensions for current DB."""

    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext"))
