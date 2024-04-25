from typing import Annotated
from uuid import UUID

from aio_pika import Channel, Message
from aio_pika.pool import Pool
from fastapi import Depends, Request
from pydantic import BaseModel

from chat_service.utils import dtos


def get_rmq_channel_pool(request: Request) -> Pool[Channel]:  # pragma: no cover
    """
    Get channel pool from the state.

    :param request: current request.
    :return: channel pool.
    """
    return request.app.state.rmq_channel_pool


class RMQService:
    """RabbitMQ Service."""

    def __init__(self, pool: Pool[Channel] = Depends(get_rmq_channel_pool)) -> None:
        self.pool = pool

    async def _publish(
        self,
        routing_key: str,
        message: BaseModel,
    ) -> None:
        """Publish message to a specific routing key."""

        async with self.pool.acquire() as conn:
            exchange = await conn.declare_exchange(
                name="",
                auto_delete=True,
            )
            await exchange.publish(
                message=Message(
                    body=message.model_dump_json().encode("utf-8"),
                    content_encoding="utf-8",
                    content_type="application/json",
                ),
                routing_key=routing_key,
            )

    async def notify_new_server_message(
        self,
        message: dtos.RMQServerNotificationDTO,
    ) -> None:
        """Notify about new server message."""

        await self._publish(
            routing_key="new_server_msg_queue",
            message=message,
        )

    async def notify_new_chat_message(
        self,
        message: dtos.RMQChatNotificationDTO,
    ) -> None:
        """Notify about new chat message."""

        await self._publish(
            routing_key="new_chat_msg_queue",
            message=message,
        )


GetRMQ = Annotated[RMQService, Depends(RMQService)]
