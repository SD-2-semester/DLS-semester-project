from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chat_service.db.dependencies import get_db_session, get_db_session_ro
from chat_service.web.daos.chat_dao import ChatReadDAO, ChatWriteDAO
from chat_service.web.daos.chat_message_dao import (
    ChatMessageReadDAO,
    ChatMessageWriteDAO,
)
from chat_service.web.daos.server_dao import ServerReadDAO, ServerWriteDAO
from chat_service.web.daos.server_member_dao import (
    ServerMemberReadDAO,
    ServerMemberWriteDAO,
)
from chat_service.web.daos.server_message_dao import (
    ServerMessageReadDAO,
    ServerMessageWriteDAO,
)


class AllReadDAOs:
    """All read only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session_ro)):
        self.session = session

    @property
    def chat(self) -> ChatReadDAO:
        return ChatReadDAO(self.session)

    @property
    def chat_message(self) -> ChatMessageReadDAO:
        return ChatMessageReadDAO(self.session)

    @property
    def server(self) -> ServerReadDAO:
        return ServerReadDAO(self.session)

    @property
    def server_message(self) -> ServerMessageReadDAO:
        return ServerMessageReadDAO(self.session)

    @property
    def server_member(self) -> ServerMemberReadDAO:
        return ServerMemberReadDAO(self.session)


class AllWriteDAOs:
    """All write only DAOs."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    @property
    def chat(self) -> ChatWriteDAO:
        return ChatWriteDAO(self.session)

    @property
    def chat_message(self) -> ChatMessageWriteDAO:
        return ChatMessageWriteDAO(self.session)

    @property
    def server(self) -> ServerWriteDAO:
        return ServerWriteDAO(self.session)

    @property
    def server_message(self) -> ServerMessageWriteDAO:
        return ServerMessageWriteDAO(self.session)

    @property
    def server_member(self) -> ServerMemberWriteDAO:
        return ServerMemberWriteDAO(self.session)


ReadDAOs = Annotated[AllReadDAOs, Depends(AllReadDAOs)]
WriteDAOs = Annotated[AllWriteDAOs, Depends(AllWriteDAOs)]
