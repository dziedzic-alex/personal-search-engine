import json
from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.auth.auth_utils import get_current_user
from api.routers.documents import router as documents_router
from db.models.document import Document, DocumentStatus, MAX_NUM_ATTEMPTS
from db.session import get_session


def make_document(**kwargs) -> Document:
    defaults = {
        "id": 1,
        "user_id": 1,
        "name": "report.pdf",
        "status": DocumentStatus.PROCESSED,
        "num_attempts": 0,
        "content_url": "/uploads/1/report.pdf",
        "thumbnail_url": "",
        "content_type": "pdf",
        "size_bytes": 1024,
        "source_created_time": None,
        "created_time": datetime(2025, 6, 1),
    }
    defaults.update(kwargs)
    return Document(**defaults)


@pytest.fixture
def documents_client(mocker, mock_user):
    mock_session = mocker.MagicMock()

    def override_get_session():
        yield mock_session

    mock_redis = mocker.MagicMock()
    mocker.patch("api.routers.documents.get_redis_client", return_value=mock_redis)

    app = FastAPI()
    app.include_router(documents_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: mock_user

    return TestClient(app), mock_session, mock_redis


def test_get_documents_returns_user_documents(documents_client, mocker):
    client, mock_session, _ = documents_client
    document = make_document()

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = [document]
    mock_session.scalars.return_value = mock_scalars

    response = client.get("/documents/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"] == [
        {
            "id": 1,
            "name": "report.pdf",
            "contentCategory": "pdf",
            "status": "processed",
            "numAttempts": 0,
            "contentUrl": "/uploads/1/report.pdf",
            "thumbnailUrl": "",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": document.created_time.isoformat(),
        }
    ]


def test_update_document_renames_document(documents_client):
    client, mock_session, _ = documents_client
    document = make_document()
    mock_session.get.return_value = document

    response = client.patch("/documents/1", json={"name": "annual report.pdf"})

    assert response.status_code == 200
    assert response.json()["name"] == "annual report.pdf"
    assert document.name == "annual report.pdf"
    mock_session.commit.assert_called_once()


def test_update_document_returns_404_when_missing(documents_client):
    client, mock_session, _ = documents_client
    mock_session.get.return_value = None

    response = client.patch("/documents/1", json={"name": "new.pdf"})

    assert response.status_code == 404


def test_update_document_returns_403_for_other_users_document(documents_client):
    client, mock_session, _ = documents_client
    mock_session.get.return_value = make_document(user_id=2)

    response = client.patch("/documents/1", json={"name": "new.pdf"})

    assert response.status_code == 403


def test_delete_document_removes_document(documents_client):
    client, mock_session, _ = documents_client
    document = make_document()
    mock_session.get.return_value = document

    response = client.delete("/documents/1")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(document)
    mock_session.commit.assert_called_once()


def test_retry_document_requeues_processing(documents_client):
    client, mock_session, mock_redis = documents_client
    document = make_document(status=DocumentStatus.FAILED, num_attempts=1)
    mock_session.get.return_value = document

    response = client.post("/documents/1/retry")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert document.status == DocumentStatus.PENDING
    mock_session.commit.assert_called_once()
    mock_redis.lpush.assert_called_once_with(
        "jobs:upload", json.dumps({"document_id": 1})
    )


def test_retry_document_returns_400_at_max_attempts(documents_client):
    client, mock_session, _ = documents_client
    mock_session.get.return_value = make_document(
        status=DocumentStatus.FAILED,
        num_attempts=MAX_NUM_ATTEMPTS,
    )

    response = client.post("/documents/1/retry")

    assert response.status_code == 400
