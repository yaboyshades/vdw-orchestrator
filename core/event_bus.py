import asyncio
import json
import logging
from typing import Callable, Dict, Any
import aioredis

class EventBus:
    """Redis-backed pub/sub EventBus with simple channel routing."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.logger = logging.getLogger(self.__class__.__name__)
        self._pub = None
        self._sub = None
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    async def connect(self):
        self._pub = await aioredis.from_url(self.redis_url, decode_responses=True)
        self._sub = await aioredis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self._sub.pubsub()
        self.logger.info(f"EventBus connected to {self.redis_url}")

    async def publish(self, topic: str, payload: Dict[str, Any]):
        if not self._pub:
            await self.connect()
        await self._pub.publish(topic, json.dumps(payload))

    async def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], Any]):
        self._handlers[topic] = handler
        if not self.pubsub:
            await self.connect()
        await self.pubsub.subscribe(topic)

    async def start(self):
        if not self.pubsub:
            await self.connect()
        asyncio.create_task(self._listen())

    async def _listen(self):
        async for message in self.pubsub.listen():
            if message.get("type") != "message":
                continue
            channel = message["channel"]
            data = json.loads(message["data"]) if message.get("data") else {}
            handler = self._handlers.get(channel)
            if handler:
                try:
                    await handler(data) if asyncio.iscoroutinefunction(handler) else handler(data)
                except Exception as e:
                    self.logger.error(f"Handler error on {channel}: {e}")
