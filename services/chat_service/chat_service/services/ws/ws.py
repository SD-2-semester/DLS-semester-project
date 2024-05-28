from typing import Annotated

from fastapi import BackgroundTasks, Depends, Request, WebSocket
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from chat_service.services.ws.ws_deps import MessageType


def get_redis(request: Request) -> Redis:  # type: ignore
    """Get redis connection."""

    return request.app.state.redis


class RedisPubSubManager:
    """Initialize the RedisPubSubManager."""

    def __init__(self, redis: Redis = Depends(get_redis)) -> None:  # type: ignore
        self.redis = redis

    async def connect(self) -> None:
        """Connects to the Redis server and initializes the pubsub client."""
        self.pubsub = self.redis.pubsub()

    async def publish(self, room_id: str, message: MessageType) -> None:
        """Publish message to a specific Redis channel."""
        await self.redis.publish(room_id, "message.model_dump_json()")

    async def subscribe(self, room_id: str) -> PubSub:
        """Subscribe to a Redis channel."""
        await self.pubsub.subscribe(room_id)
        return self.pubsub

    async def unsubscribe(self, room_id: str) -> None:
        """Unsubscribe from a Redis channel."""
        await self.pubsub.unsubscribe(room_id)


class WebSocketManager:
    """..."""

    def __init__(
        self,
        pubsub_client: RedisPubSubManager = RedisPubSubManager(),
    ) -> None:
        self.rooms: dict[str, list[WebSocket]] = {}
        self.pubsub_client = pubsub_client

    def is_user_in_room(self, user_id: str, room_id: str) -> bool:
        """..."""

        room = self.rooms.get(room_id, None)

        if room is None:
            return False

        return user_id in room

    async def connect_user(
        self,
        room_id: Annotated[str, "Chat/Server ID."],
        websocket: WebSocket,
        background_tasks: BackgroundTasks,
    ) -> None:
        """Adds a user's WebSocket connection to a room."""
        await websocket.accept()

        if room_id in self.rooms:
            self.rooms[room_id].append(websocket)
            return

        self.rooms[room_id] = [websocket]

        await self.pubsub_client.connect()
        pubsub_subscriber = await self.pubsub_client.subscribe(room_id)
        background_tasks.add_task(
            self.dispatch_pubsub_messages,
            pubsub_subscriber,
        )

    async def broadcast(self, room_id: str, message: MessageType) -> None:
        """Broadcasts a message to all connected WebSockets in a room."""
        await self.pubsub_client.publish(room_id, message)

    async def remove_user(
        self,
        room_id: str,
        websocket: WebSocket,
    ) -> None:
        """Removes a user's WebSocket connection from a room."""

        self.rooms[room_id].remove(websocket)

    async def dispatch_pubsub_messages(self, pubsub_subscriber: PubSub) -> None:
        """Reads and broadcasts messages received from Redis PubSub."""

        while True:
            message = await pubsub_subscriber.get_message(
                ignore_subscribe_messages=True
            )
            if message is not None:
                room_id = message["channel"].decode("utf-8")
                all_sockets = self.rooms[room_id]
                for socket in all_sockets:
                    data = message["data"].decode("utf-8")
                    await socket.send_text(data)


ws_manager = WebSocketManager()
