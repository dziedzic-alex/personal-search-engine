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
from shared.sqs_client import get_document_processing_sqs_client


FILE_GROUP_ID = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def mock_persist_file(mocker):
    return mocker.patch(
        "api.routers.documents.documents.persist_file",
        side_effect=lambda s3_client, file_data, user_id, content_type: (
            PersistedFileObjectKeys(
                content_key=f"{user_id}/{FILE_GROUP_ID}/content",
                thumbnail_key=f"{user_id}/{FILE_GROUP_ID}/thumbnail",
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

    mock_sqs_client = mocker.MagicMock()

    app = FastAPI()
    app.include_router(documents_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_s3_client] = lambda: mock_s3_client
    app.dependency_overrides[get_document_processing_sqs_client] = lambda: (
        mock_sqs_client
    )

    return (
        TestClient(app),
        mock_session,
        mock_sqs_client,
        mock_persist_file,
        mock_s3_client,
    )
