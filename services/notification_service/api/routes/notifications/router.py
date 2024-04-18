from fastapi import APIRouter, WebSocket
from api.routes.notifications.ws_connection_manager import ws_manager
import asyncio

router = APIRouter()


@router.get("/hello")
async def hello():
    return "hello"


@router.websocket("/notification/{user_id}")
async def sub_notifications(websocket: WebSocket, user_id: str) -> None:
    """User subscribes to notifications."""

    await ws_manager.connect(websocket, user_id)
    print("Connected: User ID", user_id)

    try:
        # task to handle incoming WebSocket messages
        consumer_task = asyncio.create_task(
            consume_websocket_messages(websocket, user_id)
        )

        # task to handle messages from Redis Pub/Sub
        producer_task = asyncio.create_task(produce_to_websocket(user_id))

        # Wait for either task to finish - if one fails or finishes, the other should be cancelled
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # If either task is done, cancel the other and handle any exceptions
        for task in pending:
            task.cancel()
        for task in done:
            if task.exception():
                raise task.exception()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await ws_manager.disconnect(websocket, user_id)
        print("Disconnected: User ID", user_id)


async def consume_websocket_messages(websocket: WebSocket, user_id: str):
    """Consume messages from the WebSocket connection and publish to Redis."""
    try:
        while True:
            data = await websocket.receive_text()
            print("Received from client:", data)
            await ws_manager.broadcast(data, user_id)
    except Exception as e:
        print(f"Error in consumer: {e}")


async def produce_to_websocket(user_id: str):
    """Listen to messages from Redis and send to WebSocket connections."""
    try:
        await ws_manager.broadcast_local(user_id)
    except Exception as e:
        print(f"Error in producer: {e}")
