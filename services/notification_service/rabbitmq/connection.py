import json
import asyncio
from aio_pika import connect, IncomingMessage, ExchangeType, RobustConnection
from api.routes.notifications.ws_connection_manager import ws_manager
from settings import settings


async def get_rabbitmq_connection() -> RobustConnection:
    """Get a connection to the message broker."""
    print(str(settings.rabbit_url))
    return await connect(str(settings.rabbit_url))


async def rabbitmq_consumer():
    connection = await get_rabbitmq_connection()
    channel = await connection.channel()
    connection = await connect(str(settings.rabbit_url))
    channel = await connection.channel()

    queue = await channel.declare_queue("new_relation_queue", durable=True)

    async def on_message(message: IncomingMessage):
        async with message.process():
            body = json.loads(message.body)
            print("🐰", body)
            user_id_1 = body.get("user_id_1")
            user_id_2 = body.get("user_id_2")

            print(ws_manager.active_connections)
            # Broadcasting to user_id_1 and user_id_2
            if user_id_1 in ws_manager.active_connections:
                await ws_manager.broadcast(
                    f"Notification for user: {user_id_1}", user_id_1
                )
            if user_id_2 in ws_manager.active_connections:
                await ws_manager.broadcast(
                    f"Notification for user: {user_id_2}", user_id_2
                )

    await queue.consume(on_message)
