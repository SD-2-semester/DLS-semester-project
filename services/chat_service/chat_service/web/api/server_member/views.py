import sqlalchemy as sa
from fastapi import APIRouter

from chat_service import exceptions
from chat_service.core.pagination_dtos import Pagination
from chat_service.db import models
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs
from chat_service.web.api.server.dependencies import GetServer, GetServerIfMember

router = APIRouter()


@router.post("/server/{server_id}", status_code=201)
async def join_server(
    server: GetServer,
    request_dto: dtos.ServerMemberRequestDTO,
    r_daos: ReadDAOs,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Join server, creating a server member record."""

    existing_member = await r_daos.server_member.filter_one(
        user_id=request_dto.user_id,
    )

    if existing_member is not None:
        raise exceptions.Http403(
            f"User with id '{request_dto.user_id}' is already a member of this server."
        )

    obj_id = await w_daos.server_member.create(
        input_dto=dtos.ServerMemberInputDTO(
            server_id=server.id, **request_dto.model_dump()
        ),
    )

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@router.get("/server/{server_id}/user/{user_id}")
async def get_members_by_server(
    server: GetServerIfMember,
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ServerMemberDTO]:
    """Get servers owned by given user."""

    query = sa.select(models.ServerMember).where(
        models.Server.id == server.id,
    )

    return await r_daos.server_member.get_offset_results(
        pagination=pagination,
        out_dto=dtos.ServerMemberDTO,
        query=query,
    )
