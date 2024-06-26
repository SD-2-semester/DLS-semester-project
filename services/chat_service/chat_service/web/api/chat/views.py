from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter

from chat_service import exceptions
from chat_service.core.pagination_dtos import Pagination
from chat_service.db.models import Chat
from chat_service.utils import dtos
from chat_service.utils.daos import ReadDAOs, WriteDAOs

router = APIRouter()


@router.post("", status_code=201)
async def create_chat(
    input_dto: dtos.ChatInputDTO,
    r_daos: ReadDAOs,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Create a chat between two users."""

    existing_chat = await r_daos.chat.filter_one(
        user_id_1=input_dto.user_id_1,
        user_id_2=input_dto.user_id_2,
    )

    if existing_chat is not None:
        raise exceptions.Http403("Chat between users already exists.")

    obj_id = await w_daos.chat.create(input_dto)

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )


@router.get("/users/{user_id}")
async def get_chats_where_is_participant(
    user_id: UUID,
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ChatDTO]:
    """Get all chats where user is a participant."""

    query = sa.select(Chat).where(
        sa.or_(
            Chat.user_id_1 == user_id,
            Chat.user_id_2 == user_id,
        )
    )

    return await r_daos.chat.get_offset_results(
        pagination=pagination,
        out_dto=dtos.ChatDTO,
        query=query,
    )


@router.get("")
async def get_all_chats(
    r_daos: ReadDAOs,
    pagination: Pagination,
) -> dtos.OffsetResults[dtos.ChatDTO]:
    """Get all chats (for testing purposes)."""

    return await r_daos.chat.get_offset_results(
        pagination=pagination, out_dto=dtos.ChatDTO
    )
