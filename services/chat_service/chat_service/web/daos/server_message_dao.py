from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import ServerMessage
from chat_service.web.dtos.server_message_dtos import ServerMessageInputDTO


class ServerMessageReadDAO(BaseDAORO[ServerMessage]):
    """Class for accessing ServerMessage table READ."""


class ServerMessageWriteDAO(
    ServerMessageReadDAO, BaseDAOWO[ServerMessage, ServerMessageInputDTO]
):
    """Class for accessing ServerMessage table WRITE."""
