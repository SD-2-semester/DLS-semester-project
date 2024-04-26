from chat_service.core.base_dao import BaseDAORO, BaseDAOWO
from chat_service.db.models import ServerMember
from chat_service.web.dtos.server_member_dtos import ServerMemberInputDTO


class ServerMemberReadDAO(BaseDAORO[ServerMember]):
    """Class for accessing ServerMember table READ."""


class ServerMemberWriteDAO(
    ServerMemberReadDAO, BaseDAOWO[ServerMember, ServerMemberInputDTO]
):
    """Class for accessing ServerMember table WRITE."""
