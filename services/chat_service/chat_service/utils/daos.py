from typing import Annotated
from chat_service.web.daos.chat_dao import ChatReadDAO
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from chat_service.db.dependencies import get_db_session_ro


class AllReadDAOs:
    """All read only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session_ro)):
        self.session = session

    @property
    def chat(self) -> ChatReadDAO:
        return ChatReadDAO(self.session)


class AllWriteDAOs:
    """All write only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session_ro)):
        self.session = session


ReadDAOs = Annotated[AllReadDAOs, Depends(AllReadDAOs)]
WriteDAOs = Annotated[AllWriteDAOs, Depends(AllWriteDAOs)]
