from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter

from chat_service.core.pagination_dtos import Pagination
from chat_service.db import models
from chat_service.services.elasticsearch.dependencies import GetES
from chat_service.services.rabbit.dependencies import GetRMQ
from chat_service.services.ws.ws import ws_manager
from chat_service.settings import settings
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs
from chat_service.utils.http import GetHttpClient
from chat_service.web.api.server.dependencies import GetServerIfMember

router = APIRouter()


@router.post(
    "/servers/{server_id}/users/{user_id}",
    status_code=201,
)
async def create_server_message(
    server: GetServerIfMember,
    elastic: GetES,
    rmq: GetRMQ,
    http_client: GetHttpClient,
    user_id: UUID,
    request_dto: dtos.ServerMessageRequestDTO,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Create server message."""

    obj_id = await w_daos.server_message.create(
        input_dto=dtos.ServerMessageInputDTO(
            server_id=server.id, **request_dto.model_dump()
        ),
    )

    await ws_manager.broadcast(
        str(server.id),
        message=dtos.ServerPublishDTO(
            message=request_dto.message,
            server_id=server.id,
        ),
    )

    await elastic.post_message(
        index="server_message",
        dto=dtos.ServerElasticCreateDTO(
            server_id=server.id,
            message=request_dto.message,
        ),
    )

    user_info = (
        await http_client.get(
            f"{settings.auth_service_url}/users/{user_id}",
        )
    )["data"]

    await rmq.notify_new_server_message(
        message=dtos.RMQServerNotificationDTO(
            server_id=server.id,
            user_id=user_id,
            message=request_dto.message,
            sender_username=user_info["username"],
        ),
    )

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@router.get("/servers/{server_id}")
async def get_messages_by_server(
    server: GetServerIfMember,
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ServerMessageDTO]:
    """Get messages by given server."""

    query = sa.select(models.ServerMessage).where(
        models.ServerMessage.server_id == server.id,
    )

    return await r_daos.server_message.get_offset_results(
        pagination=pagination,
        out_dto=dtos.ServerMessageDTO,
        query=query,
    )
