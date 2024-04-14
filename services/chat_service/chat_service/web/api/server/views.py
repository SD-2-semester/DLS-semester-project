from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter

from chat_service import exceptions
from chat_service.core.pagination_dtos import Pagination
from chat_service.db import models
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs

router = APIRouter()


@router.post("", status_code=201)
async def create_server(
    input_dto: dtos.ServerInputDTO,
    r_daos: ReadDAOs,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Create a server."""

    existing_server = await r_daos.server.filter_one(title=input_dto.title)

    if existing_server is not None:
        raise exceptions.Http403(
            f"Server with title '{input_dto.title}' already exists."
        )

    obj_id = await w_daos.server.create(input_dto)

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@router.get("/user/{user_id}")
async def get_servers_where_is_member(
    user_id: UUID,
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ServerDTO]:
    """Get servers that a given user is a member of."""

    query = (
        sa.select(models.Server)
        .join(
            models.ServerMember,
            models.Server.id == models.ServerMember.server_id,
        )
        .where(models.ServerMember.user_id == user_id)
    )

    return await r_daos.server.get_offset_results(
        pagination=pagination,
        out_dto=dtos.ServerDTO,
        query=query,
    )
