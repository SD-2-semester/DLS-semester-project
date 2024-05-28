from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter

from chat_service.core.pagination_dtos import Pagination
from chat_service.db.models import Chat, ChatMessage
from chat_service.services.elasticsearch.dependencies import GetES
from chat_service.services.rabbit.dependencies import GetRMQ
from chat_service.services.ws.ws import ws_manager
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs
from chat_service.utils.http import GetHttpClient
from chat_service.web.api.chat.dependencies import GetChatIfParticipant

router = APIRouter()

_path = "/chats/{chat_id}/users/{user_id}"


@router.post(_path, status_code=201)
async def create_chat_message(
    chat: GetChatIfParticipant,
    elastic: GetES,
    rmq: GetRMQ,
    http_client: GetHttpClient,
    user_id: UUID,
    request_dto: dtos.ChatMessageRequestDTO,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Create message in a given chat."""

    obj_id = await w_daos.chat_message.create(
        input_dto=dtos.ChatMessageInputDTO(
            chat_id=chat.id,
            **request_dto.model_dump(),
        ),
    )

    other_user_id = chat.user_id_1 if chat.user_id_1 == user_id else chat.user_id_2
    if ws_manager.is_user_in_room(str(other_user_id), str(chat.id)):
        await ws_manager.broadcast(
            str(chat.id),
            message=dtos.ChatPublishDTO(
                message=request_dto.message,
                chat_id=chat.id,
            ),
        )

    await elastic.post_message(
        index="chat_message",
        dto=dtos.ChatElasticCreateDTO(
            chat_id=chat.id,
            message=request_dto.message,
        ),
    )

    # user_info = (
    #     await http_client.get(
    #         f"{settings.auth_service_url}/users/{user_id}",
    #     )
    # )["data"]

    await rmq.notify_new_chat_message(
        message=dtos.RMQChatNotificationDTO(
            chat_id=chat.id,
            user_id_1=chat.user_id_1,
            user_id_2=chat.user_id_2,
            message=request_dto.message,
            sender_username='user_info["username"]',
        ),
    )

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@router.get(_path)
async def get_messages_by_chat(
    chat: GetChatIfParticipant,
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ChatMessageDTO]:
    """Get messages by given chat."""

    query = (
        sa.select(ChatMessage)
        .join(
            Chat,
            ChatMessage.chat_id == Chat.id,
        )
        .where(
            ChatMessage.chat_id == chat.id,
        )
    )

    return await r_daos.chat_message.get_offset_results(
        pagination=pagination,
        out_dto=dtos.ChatMessageDTO,
        query=query,
    )
