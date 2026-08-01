from src.core.redis import redis_client
from src.shared.infra.cache import InMemoryCache, MultiLevelCache, RedisCache

in_memory_cache = InMemoryCache()

redis_cache = RedisCache(redis_client)

multi_level_cache = MultiLevelCache(l1_cache=in_memory_cache, l2_cache=redis_cache)
