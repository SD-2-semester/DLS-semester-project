from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from chat_service.db.dependencies import get_db_session


class RoDAO:
    """All read only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session


class WoDAO:
    """All write only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
