from redis.asyncio import Redis

from .config import redis_config

redis_client = Redis(
    host=redis_config.host,
    port=redis_config.port,
    db=redis_config.db,
    decode_responses=True,
)

__all__ = ["redis_client"]
