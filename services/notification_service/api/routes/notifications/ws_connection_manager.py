import uuid
from redis import asyncio as aioredis
from fastapi import WebSocket
from settings import settings


class NotificationConnectionManager:
    """Connection manager for notifications using Redis and local storage for WebSocket instances."""

    def __init__(self, redis_url: str) -> None:
        # Set up the Redis connection pool
        self.pool = aioredis.ConnectionPool.from_url(
            redis_url, max_connections=settings.redis.pool_size, decode_responses=True
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)
        self.local_connections: dict = (
            {}
        )  # Stores WebSocket instances by user_id and connection_id

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        connection_id = str(uuid.uuid4())  # Generate a unique ID for the connection
        if user_id not in self.local_connections:
            self.local_connections[user_id] = {}
        self.local_connections[user_id][connection_id] = websocket
        await self.redis.sadd(f"connections:{user_id}", connection_id)

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        # Find the connection_id
        for conn_id, ws in self.local_connections.get(user_id, {}).items():
            if ws == websocket:
                await self.redis.srem(f"connections:{user_id}", conn_id)
                del self.local_connections[user_id][conn_id]
                break
        if not self.local_connections[user_id]:
            del self.local_connections[user_id]

    async def broadcast(self, message: str, user_id: str) -> None:
        """Broadcast messages to all active WebSocket connections for a specific user."""
        connection_ids = await self.redis.smembers(f"connections:{user_id}")
        for conn_id in connection_ids:
            websocket = self.local_connections[user_id].get(conn_id)
            if websocket:
                await websocket.send_text(message)


# Initialize the WebSocket manager with the Redis URL
ws_manager = NotificationConnectionManager(redis_url=settings.redis.url)
