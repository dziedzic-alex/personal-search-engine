import redis
import os

def get_redis_client() -> redis.Redis:
    return redis.Redis.from_url(os.getenv("REDIS_URL"))
