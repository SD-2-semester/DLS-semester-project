from typing import Annotated
from uuid import UUID

from aio_pika import Channel, Message
from aio_pika.pool import Pool
from fastapi import Depends, Request

from chat_service.web.api.rabbit.schema import RMQMessageDTO


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
        message: str,
        exchange_name: str = "",
    ) -> None:
        """Publish message to a specific routing key."""

        async with self.pool.acquire() as conn:
            exchange = await conn.declare_exchange(
                name=exchange_name,
                auto_delete=True,
            )
            await exchange.publish(
                message=Message(
                    body=message.encode("utf-8"),
                    content_encoding="utf-8",
                    content_type="text/plain",
                ),
                routing_key=routing_key,
            )

    async def notify_new_server_message(
        self,
        server_id: UUID,
    ) -> None:
        """Notify about new server message."""

        await self._publish(
            routing_key="new_server_msg_queue",
            message=server_id.hex,
        )

    async def notify_new_chat_message(
        self,
        chat_id: UUID,
    ) -> None:
        """Notify about new chat message."""

        await self._publish(
            routing_key="new_chat_msg_queue",
            message=chat_id.hex,
        )


GetRMQ = Annotated[RMQService, Depends(RMQService)]
