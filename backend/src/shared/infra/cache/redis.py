import logging
import uuid

from redis.asyncio import Redis

from .base import Cache

logger = logging.getLogger(__name__)


def build_key(prefix: str, uid: uuid.UUID) -> str:
    return f"{prefix}:{uid}"


class Serializer[T](Protocol):

    def dumps(self, value: T) -> bytes: ...

    def loads(self, value: bytes) -> T: ...


class RedisCache[T](Cache[T]):
    serializer: Serializer[T]

    def __init__(self, redis: Redis, ttl: int | None = None) -> None:
        self.redis = redis
        self.ttl = ttl

    async def get(self, key: str) -> T | None:
        if (raw := await self.redis.get(key)) is None:
            return None

        return self.serializer.loads(raw)

    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        raw = self.serializer.dumps(value)

        effective_ttl = ttl if ttl is not None else self.ttl

        await self.redis.set(key, raw, ex=effective_ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        result = await self.redis.exists(key)
        return result > 0
