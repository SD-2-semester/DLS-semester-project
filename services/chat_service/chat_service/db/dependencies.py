from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_db_session_ro(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_ro_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()


async def get_db_session_wo(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session (WRITE)."""
    session: AsyncSession = request.app.state.db_session_wo_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
