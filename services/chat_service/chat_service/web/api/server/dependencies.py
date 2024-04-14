from typing import Annotated
from uuid import UUID

from fastapi import Depends

from chat_service import exceptions
from chat_service.db.models import Server
from chat_service.utils.daos import ReadDAOs


async def get_server(server_id: UUID, r_daos: ReadDAOs) -> Server:
    """Get server by id."""

    server = await r_daos.server.filter_one(id=server_id)

    if server is None:
        raise exceptions.Http404(f"Server with id '{server_id}' not found.")

    return server


GetServer = Annotated[Server, Depends(get_server)]
