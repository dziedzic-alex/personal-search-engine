import redis

from shared.settings import settings

client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global client
    if client is None:
        client = redis.Redis.from_url(settings.redis_url)
    return client
