import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.user import router as user_router

USER_ROUTES = [
    pytest.param(
        "patch",
        "/user/me",
        {"json": {"firstName": "Test", "lastName": "User"}},
        id="update",
    ),
    pytest.param("delete", "/user/me", {}, id="delete"),
]


@pytest.fixture
def unauthenticated_user_client():
    app = FastAPI()
    app.include_router(user_router)
    return TestClient(app)


@pytest.mark.parametrize("method, path, kwargs", USER_ROUTES)
def test_user_routes_require_auth(unauthenticated_user_client, method, path, kwargs):
    response = getattr(unauthenticated_user_client, method)(path, **kwargs)

    assert response.status_code == 401
