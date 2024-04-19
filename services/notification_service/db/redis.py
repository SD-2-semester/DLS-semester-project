import redis.asyncio as aioredis
from settings import settings


class RedisPubSubManager:
    """
    Initializes the RedisPubSubManager.
    """

    def __init__(self):
        self.redis_host = settings.redis.host
        self.redis_port = settings.redis.port
        self.pubsub = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        """
        Establishes a connection to Redis.
        """

        return aioredis.Redis(
            host=self.redis_host, port=self.redis_port, auto_close_connection_pool=False
        )

    async def connect(self) -> None:
        """
        Connects to the Redis server and initializes the pubsub client.
        """

        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def publish(self, user_id: str, message: str) -> None:
        """
        Publishes a message to a specific Redis channel.
        """

        await self.redis_connection.publish(user_id, message)

    async def subscribe(self, user_id: str) -> aioredis.Redis:
        """
        Subscribes to a Redis channel.
        """

        await self.pubsub.subscribe(user_id)
        return self.pubsub

    async def unsubscribe(self, user_id: str) -> None:
        """
        Unsubscribes from a Redis channel.
        """

        await self.pubsub.unsubscribe(user_id)
