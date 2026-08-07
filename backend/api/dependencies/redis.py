from typing import Annotated
from fastapi import Depends
from redis import Redis
from shared.redis_client import get_redis_client

RedisClientDep = Annotated[Redis, Depends(get_redis_client)]
