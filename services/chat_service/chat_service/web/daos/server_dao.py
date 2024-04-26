from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import Server
from chat_service.web.dtos.server_dtos import ServerInputDTO


class ServerReadDAO(BaseDAORO[Server]):
    """Class for accessing Server table READ."""


class ServerWriteDAO(ServerReadDAO, BaseDAOWO[Server, ServerInputDTO]):
    """Class for accessing Server table WRITE."""
