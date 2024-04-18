import uuid
from redis import asyncio as aioredis
from fastapi import WebSocket
from settings import settings


class NotificationConnectionManager:
    """
    Connection manager for notifications using Redis with Pub/Sub
    and local storage, for web sockets.
    """

    def __init__(self, redis_url: str) -> None:

        # Set up the Redis connection pool
        self.pool = aioredis.ConnectionPool.from_url(
            redis_url, max_connections=settings.redis.pool_size, decode_responses=True
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)

        # set up pub/sub
        self.pubsub = self.redis.pubsub()

        # stores WebSocket instances by user_id and connection_id
        # so we can check is user is connected in the current pod
        self.local_connections: dict = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Creates a websocket connection in the redis db, and locally.
        And then subscribes to the redis channel.
        """

        await websocket.accept()

        # Generate a unique ID for the connection
        connection_id = str(uuid.uuid4())

        if user_id not in self.local_connections:
            self.local_connections[user_id] = {}

        self.local_connections[user_id][connection_id] = websocket

        await self.redis.sadd(f"connections:{user_id}", connection_id)  # type: ignore

        # Subscribe to the user's channel
        await self.pubsub.subscribe(user_id)

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Disconnects the user, and deletes him from Redis,
        user is also unsubscribed from channel.
        """

        for conn_id, ws in self.local_connections.get(user_id, {}).items():
            if ws == websocket:
                await self.redis.srem(f"connections:{user_id}", conn_id)  # type: ignore
                del self.local_connections[user_id][conn_id]
                break
        if not self.local_connections[user_id]:
            await self.pubsub.unsubscribe(user_id)
            del self.local_connections[user_id]

    async def broadcast(self, message: str, user_id: str) -> None:
        """
        Broadcast messages to all active WebSocket connections
        for a specific user using Pub/Sub.
        """

        await self.redis.publish(user_id, message)

    async def broadcast_local(self, user_id: str) -> None:
        """
        Handle received messages from Pub/Sub and send
        to local WebSocket connections.
        """

        async for message in self.pubsub.listen():
            if message["type"] == "message" and message["channel"] == user_id:
                if user_id in self.local_connections:
                    for conn_id in self.local_connections[user_id]:
                        websocket = self.local_connections[user_id][conn_id]
                        if websocket:
                            await websocket.send_text(message["data"])


# Initialize the WebSocket manager with the Redis URL
ws_manager = NotificationConnectionManager(redis_url=settings.redis.url)
