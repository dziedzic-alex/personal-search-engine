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

    redis_store: dict[str, bytes] = {}

    def redis_set(key, value, ex=None):
        if isinstance(value, bytes):
            redis_store[key] = value
        else:
            redis_store[key] = str(value).encode()

    mock_redis = mocker.MagicMock()
    mock_redis.set.side_effect = redis_set
    mock_redis.get.side_effect = lambda key: redis_store.get(key)
    mock_redis.delete.side_effect = lambda key: redis_store.pop(key, None)
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
