from typing import Annotated
from uuid import UUID

from fastapi import Depends

from chat_service import exceptions
from chat_service.db.models import Server
from chat_service.utils.daos import ReadDAOs


async def get_server(server_id: UUID, r_daos: ReadDAOs) -> Server:
    """Get server by id."""

    return await r_daos.server.get_by_id_or_error(id=server_id)


GetServer = Annotated[Server, Depends(get_server)]


async def get_server_if_member(
    server: GetServer, user_id: UUID, r_daos: ReadDAOs
) -> Server:
    """Get server if member."""

    existing_member = await r_daos.server_member.filter_one(user_id=user_id)

    if existing_member is None:
        raise exceptions.Http404("User is not a member of this server.")

    return server


GetServerIfMember = Annotated[Server, Depends(get_server_if_member)]
