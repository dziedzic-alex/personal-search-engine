import redis
import os

client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global client
    if client is None:
        client = redis.Redis.from_url(os.getenv("REDIS_URL"))
    return client
