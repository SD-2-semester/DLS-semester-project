from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat_service.db.dependencies import get_db_session, get_db_session_ro
from chat_service.web.daos.chat_dao import ChatReadDAO, ChatWriteDAO


class AllReadDAOs:
    """All read only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session_ro)):
        self.session = session

    @property
    def chat(self) -> ChatReadDAO:
        return ChatReadDAO(self.session)


class AllWriteDAOs:
    """All write only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    @property
    def chat(self) -> ChatWriteDAO:
        return ChatWriteDAO(self.session)


ReadDAOs = Annotated[AllReadDAOs, Depends(AllReadDAOs)]
WriteDAOs = Annotated[AllWriteDAOs, Depends(AllWriteDAOs)]
