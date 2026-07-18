import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.auth.auth_utils import get_current_user
from api.routers.user import router as user_router
from db.session import get_session
from shared.s3_client import get_s3_client
from tests.api.conftest import make_user


@pytest.fixture
def user_client(mocker):
    mock_session = mocker.MagicMock()
    mock_s3_client = mocker.MagicMock()
    user = make_user()

    def override_get_session():
        yield mock_session

    app = FastAPI()
    app.include_router(user_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client

    return TestClient(app), mock_session, mock_s3_client, user
