from datetime import datetime

import pytest
from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers import search
from api.routers.auth.auth_utils import get_current_user
from api.routers.upload.upload import router as upload_router
from api.routers.upload.upload_utils import PersistedFileObjectKeys
from db.models.document import DocumentStatus
from db.models.user import User, UserPlan
from db.session import get_session
from shared.s3_client import get_s3_client

ph = PasswordHasher()


@pytest.fixture
def mock_s3_client(mocker):
    client = mocker.MagicMock()
    client.generate_presigned_url.side_effect = lambda object_key, expires_in=3600: (
        f"https://presigned.example/{object_key}"
    )
    client.delete_file = mocker.MagicMock()
    client.get_file = mocker.MagicMock(return_value=b"")
    return client


@pytest.fixture
def mock_user() -> User:
    return User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password="hashed",
        plan=UserPlan.FREE,
    )


def make_user(**kwargs) -> User:
    defaults = {
        "id": 1,
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": ph.hash("password123"),
        "plan": UserPlan.FREE,
    }
    defaults.update(kwargs)
    return User(**defaults)


@pytest.fixture
def mock_persist_file(mocker):
    return mocker.patch(
        "api.routers.upload.upload.persist_file",
        side_effect=lambda s3_client, filename, file_data, user_id, content_type: (
            PersistedFileObjectKeys(
                content_key=f"{user_id}/{filename}",
                thumbnail_key=f"{user_id}/thumbnail_{filename.rsplit('.', 1)[0]}.jpg",
            )
        ),
    )


@pytest.fixture
def upload_client(mocker, mock_user, mock_s3_client, mock_persist_file):
    mock_session = mocker.MagicMock()
    next_document_id = 1

    def assign_document_id(document):
        nonlocal next_document_id
        document.id = next_document_id
        if document.status is None:
            document.status = DocumentStatus.PENDING
        if document.num_attempts is None:
            document.num_attempts = 0
        if document.created_time is None:
            document.created_time = datetime(2025, 6, 17)
        next_document_id += 1

    mock_session.add.side_effect = assign_document_id
    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = None
    mock_session.scalars.return_value = mock_scalars

    def override_get_session():
        yield mock_session

    mock_redis = mocker.MagicMock()
    mocker.patch("api.routers.upload.upload.get_redis_client", return_value=mock_redis)

    app = FastAPI()
    app.include_router(upload_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client

    return TestClient(app), mock_session, mock_redis, mock_persist_file, mock_s3_client


@pytest.fixture
def search_client(mocker, mock_user):
    mock_session = mocker.MagicMock()

    def override_get_session():
        yield mock_session

    mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_text_documents",
        return_value=[],
    )
    mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_image_documents",
        return_value=[],
    )

    app = FastAPI()
    app.include_router(search.router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    return TestClient(app)
