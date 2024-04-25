from typing import AsyncGenerator

from sqlalchemy import exc as sa_exc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_db_session_ro(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session (READ)."""
    session: AsyncSession = request.app.state.db_session_ro_factory()

    try:
        yield session
    except sa_exc.DBAPIError:
        await session.rollback()
        raise
    finally:
        await session.commit()
        await session.close()


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session (WRITE)."""
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    except sa_exc.DBAPIError:
        await session.rollback()
        raise
    finally:
        await session.commit()
        await session.close()
