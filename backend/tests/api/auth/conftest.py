import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.auth.auth import router as auth_router
from db.session import get_session


@pytest.fixture
def auth_client(mocker):
    mocker.patch(
        "api.routers.auth.auth_utils.settings.jwt_secret",
        "test-jwt-secret-that-is-long-enough",
    )

    redis_store: dict[str, str] = {}
    mock_redis = mocker.MagicMock()
    mock_redis.set.side_effect = (
        lambda key, value, ex=None: redis_store.__setitem__(key, str(value))
    )
    mock_redis.get.side_effect = lambda key: redis_store.get(key)
    mock_redis.delete.side_effect = lambda key: redis_store.pop(key, None)
    mocker.patch(
        "api.routers.auth.auth_utils.get_redis_client",
        return_value=mock_redis,
    )

    mock_session = mocker.MagicMock()

    def override_get_session():
        yield mock_session

    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_session] = override_get_session

    return TestClient(app), mock_session, redis_store
