from db.redis import RedisPubSubManager
import asyncio
import redis.asyncio as aioredis
import json
from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        """
        Initializes the WebSocketManager.
        With a dict to store WebSocket connections by user ID.
        An instance of the RedisPubSubManager class for pub-sub functionality
        is also created.
        """

        self.connections: dict = {}
        self.pubsub_client = RedisPubSubManager()

    async def connect_user(self, user_id: str, websocket: WebSocket) -> None:
        """
        Connects a user's WebSocket and subscribes them to their
        notification channel by user_id.
        """

        await websocket.accept()

        if user_id not in self.connections:
            self.connections[user_id] = []

        self.connections[user_id].append(websocket)

        # Connect to Redis and subscribe to the user's channel
        await self.pubsub_client.connect()
        pubsub_subscriber = await self.pubsub_client.subscribe(user_id)
        asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber, user_id))

    async def send_notification(self, user_id: str, message: str) -> None:
        """
        Sends a notification message to a specific user's channel.
        """

        await self.pubsub_client.publish(user_id, message)

    async def disconnect_user(self, user_id: str, websocket: WebSocket) -> None:
        """
        Disconnects a user's WebSocket connection and unsubscribes them
        if it's the last connection.
        """

        self.connections[user_id].remove(websocket)

        if len(self.connections[user_id]) == 0:
            del self.connections[user_id]
            await self.pubsub_client.unsubscribe(user_id)

    async def _pubsub_data_reader(
        self, pubsub_subscriber: RedisPubSubManager, user_id: str
    ) -> None:
        """
        Reads messages from Redis PubSub and sends them to
        the user's WebSocket connections.
        """

        while True:
            message = await pubsub_subscriber.get_message(
                ignore_subscribe_messages=True
            )
            if message is not None:
                data = message["data"].decode("utf-8")
                for websocket in self.connections[user_id]:
                    await websocket.send_text(data)


ws_manager = WebSocketManager()
