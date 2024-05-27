from uuid import UUID

from fastapi import APIRouter, Query

from chat_service.services.elasticsearch.dependencies import GetES
from chat_service.services.rabbit.dependencies import GetRMQ
from chat_service.utils import dtos

router = APIRouter()


@router.post("/es")
async def demo_post_message(
    elastic: GetES,
    message: dtos.ServerElasticCreateDTO,
) -> dtos.ServerElasticCreateDTO:
    """
    Demo post message.

    :returns: posted message.
    """
    await elastic.post_message(index="server_message", dto=message)
    return message


@router.get("/es/{server_id}")
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


@router.post("/rmq")
async def demo_notify_new_server_message(
    rmq: GetRMQ,
    message: dtos.RMQServerNotificationDTO,
) -> dtos.RMQServerNotificationDTO:
    """
    Demo notify new server message.

    :returns: notified message.
    """
    await rmq.notify_new_server_message(message=message)
    return message
