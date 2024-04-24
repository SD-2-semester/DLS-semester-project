from uuid import UUID

from fastapi import APIRouter, Depends, Query

from chat_service.services.elasticsearch.dependencies import GetES
from chat_service.utils import dtos
from chat_service.web.api.echo.schema import Message

router = APIRouter()


@router.post("/", response_model=Message)
async def demo_post_message(
    elastic: GetES,
    message: dtos.ServerElasticDTO,
) -> dtos.ServerElasticDTO:
    """
    Demo post message.

    :returns: None.
    """
    await elastic.post_message(index="server_message", dto=message)
    return message


@router.get("/{server_id}")
async def demo_get_messages(
    elastic: GetES,
    server_id: UUID,
    search: str = Query(...),
) -> list[dtos.ServerElasticDTO]:
    """
    Demo get messages.

    :returns: list of messages.
    """
    return await elastic.search_messages(
        obj_id=server_id,
        index="server_message",
        message=search,
        out_dto=dtos.ServerElasticDTO,
    )
