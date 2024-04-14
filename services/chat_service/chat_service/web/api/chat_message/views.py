import sqlalchemy as sa
from fastapi import APIRouter

from chat_service.core.pagination_dtos import Pagination
from chat_service.db.models import Chat, ChatMessage
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs
from chat_service.web.api.chat.dependencies import GetChatIfParticipant

router = APIRouter()

_path = "/chat/{chat_id}/user/{user_id}"


@router.post(_path, status_code=201)
async def create_chat_message(
    chat: GetChatIfParticipant,
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

    # TODO: websocket, notification

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
