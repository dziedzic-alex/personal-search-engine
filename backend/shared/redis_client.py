from redis import Redis

from shared.settings import settings

client: Redis | None = None


def get_redis_client() -> Redis:
    global client
    if client is None:
        client = Redis.from_url(settings.redis_url)
    return client
