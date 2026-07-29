import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies.ses import get_ses_client
from api.routers.auth.auth import router as auth_router
from db.session import get_session


@pytest.fixture
def auth_client(mocker):
    mocker.patch(
        "api.routers.auth.auth_utils.settings.jwt_secret",
        "test-jwt-secret-that-is-long-enough",
    )
    mocker.patch(
        "api.routers.auth.auth.settings.frontend_base_url",
        "http://localhost:5173",
    )

    # String keys hold bytes (verification/reset tokens).
    # Hash keys hold dict[str, bytes] (refresh token fields).
    redis_store: dict[str, bytes | dict[str, bytes]] = {}

    def _as_bytes(value) -> bytes:
        if isinstance(value, bytes):
            return value
        return str(value).encode()

    def redis_set(key, value, ex=None):
        redis_store[key] = _as_bytes(value)

    def redis_get(key):
        value = redis_store.get(key)
        if isinstance(value, dict):
            return None
        return value

    def redis_delete(*keys):
        deleted = 0
        for key in keys:
            if key in redis_store:
                del redis_store[key]
                deleted += 1
        return deleted

    def redis_hset(name, key=None, value=None, mapping=None, items=None):
        hash_map = redis_store.get(name)
        if not isinstance(hash_map, dict):
            hash_map = {}
            redis_store[name] = hash_map

        if mapping:
            for field, field_value in mapping.items():
                hash_map[field] = _as_bytes(field_value)
        if items:
            for i in range(0, len(items), 2):
                hash_map[items[i]] = _as_bytes(items[i + 1])
        if key is not None:
            hash_map[key] = _as_bytes(value)
        return 1

    def redis_hexists(name, key):
        hash_map = redis_store.get(name)
        if not isinstance(hash_map, dict):
            return False
        return key in hash_map

    def redis_hdel(name, *fields):
        hash_map = redis_store.get(name)
        if not isinstance(hash_map, dict):
            return 0

        deleted = 0
        for field in fields:
            if field in hash_map:
                del hash_map[field]
                deleted += 1

        if not hash_map:
            redis_store.pop(name, None)

        return deleted

    def redis_hexpire(name, seconds, *fields, **kwargs):
        return [1 for _ in fields]

    mock_redis = mocker.MagicMock()
    mock_redis.set.side_effect = redis_set
    mock_redis.get.side_effect = redis_get
    mock_redis.delete.side_effect = redis_delete
    mock_redis.hset.side_effect = redis_hset
    mock_redis.hexists.side_effect = redis_hexists
    mock_redis.hdel.side_effect = redis_hdel
    mock_redis.hexpire.side_effect = redis_hexpire
    mocker.patch(
        "api.routers.auth.auth_utils.get_redis_client",
        return_value=mock_redis,
    )
    mocker.patch(
        "api.routers.auth.auth.get_redis_client",
        return_value=mock_redis,
    )

    mock_ses = mocker.MagicMock()
    mock_session = mocker.MagicMock()

    def override_get_session():
        yield mock_session

    def override_get_ses_client():
        return mock_ses

    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_ses_client] = override_get_ses_client

    return TestClient(app), mock_session, redis_store, mock_ses
