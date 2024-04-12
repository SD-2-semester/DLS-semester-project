from uuid import UUID

from chat_service import exceptions
from chat_service.utils import dtos
from fastapi import APIRouter, Depends
from typing import Annotated

from chat_service.utils.daos import ReadDAOs, WriteDAOs

router = APIRouter()


@router.post("", status_code=201)
async def create_chat(
    input_dto: dtos.ChatInputDTO,
    r_daos: ReadDAOs,
    w_daos: WriteDAOs,
) -> dtos.DefaultCreatedResponse:
    """Create a chat between two users."""

    db_obj = await r_daos.chat.get_chat(
        user_id_1=input_dto.user_id_1,
        user_id_2=input_dto.user_id_2,
    )

    if db_obj:
        raise exceptions.Http403("Chat between users already exists.")

    obj_id = await w_daos.chat.create(input_dto)

    return dtos.DefaultCreatedResponse(
        data=dtos.CreatedResponse(id=obj_id),
    )
