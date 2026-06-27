from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.auth.auth_utils import get_current_user
from api.routers.documents.documents import router as documents_router
from api.routers.documents.upload_utils import PersistedFileObjectKeys
from db.models.document import DocumentStatus
from db.session import get_session
from shared.s3_client import get_s3_client


@pytest.fixture
def mock_persist_file(mocker):
    return mocker.patch(
        "api.routers.documents.documents.persist_file",
        side_effect=lambda s3_client, filename, file_data, user_id, content_type: (
            PersistedFileObjectKeys(
                content_key=f"{user_id}/{filename}",
                thumbnail_key=f"{user_id}/thumbnail_{filename.rsplit('.', 1)[0]}.jpg",
            )
        ),
    )


@pytest.fixture
def documents_client(mocker, mock_user, mock_s3_client, mock_persist_file):
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
    mock_scalars.all.return_value = []
    mock_session.scalars.return_value = mock_scalars

    def override_get_session():
        yield mock_session

    mock_redis = mocker.MagicMock()
    mocker.patch(
        "api.routers.documents.documents.get_redis_client", return_value=mock_redis
    )

    app = FastAPI()
    app.include_router(documents_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client

    return TestClient(app), mock_session, mock_redis, mock_persist_file, mock_s3_client
