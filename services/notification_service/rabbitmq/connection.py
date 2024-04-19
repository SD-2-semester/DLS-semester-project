import json
import asyncio
from aio_pika import connect, IncomingMessage, ExchangeType, RobustConnection
from api.routes.notifications.ws_connection_manager import ws_manager
from settings import settings
from enum import Enum, auto


class QueueType(Enum):
    """Enum for different queues in rabbit mq."""

    NEW_RELATION = auto()
    NEW_CHAT = auto()

    @staticmethod
    def get_queue_name(queue_type):
        """Get the queue name for the rabbitmq queue."""

        queue_names = {
            QueueType.NEW_RELATION: "new_relation_queue",
            QueueType.NEW_CHAT: "new_chat_queue",
        }
        return queue_names.get(queue_type)

    @staticmethod
    def get_message_template(queue_type):
        """Get the message template based on the queue."""

        message_templates = {
            QueueType.NEW_RELATION: "You are now friends with: {0}",
            QueueType.NEW_CHAT: "You have received a new message from: {0}",
        }
        return message_templates.get(queue_type)


async def get_rabbitmq_connection() -> RobustConnection:
    """Create a connection to rabbitmq."""

    return await connect(str(settings.rabbit_url))  # type: ignore


async def declare_and_consume(queue_type):
    """
    Declare the queue, and start consuming it.
    When a message is received notify the user.
    """

    message_template = QueueType.get_message_template(queue_type)
    if message_template:
        connection = await get_rabbitmq_connection()
        channel = await connection.channel()
        queue_name = QueueType.get_queue_name(queue_type)
        queue = await channel.declare_queue(queue_name, durable=True)
        # start consuming
        await queue.consume(create_message_handler(message_template))


def create_message_handler(notification_message):
    """Create message handler."""

    async def on_message(message: IncomingMessage):
        """Notify user."""

        async with message.process():
            body = json.loads(message.body)
            user_id = body.get("user_id_2")
            if user_id:
                await ws_manager.send_notification(
                    message=notification_message.format(body.get("user_id_1")),
                    user_id=user_id,
                )

    return on_message


async def setup_rabbitmq_consumers():
    """Setup the consumers."""
    await declare_and_consume(QueueType.NEW_RELATION)
    await declare_and_consume(QueueType.NEW_CHAT)
