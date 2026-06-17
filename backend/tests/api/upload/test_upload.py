import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.upload.upload import router as upload_router


def test_upload_requires_auth(mocker, tmp_path):
    mocker.patch("api.routers.upload.upload.UPLOAD_DIR", tmp_path)
    mocker.patch("api.routers.upload.upload.get_redis_client")

    app = FastAPI()
    app.include_router(upload_router)
    client = TestClient(app)

    response = client.post(
        "/upload/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 401


def test_upload_returns_files_being_processed(upload_client):
    client, mock_session, mock_redis = upload_client

    response = client.post(
        "/upload/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "files_being_processed": [{"filename": "test.pdf", "status": "pending"}]
    }
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_redis.lpush.assert_called_once_with(
        "jobs:upload", json.dumps({"document_id": 1})
    )


def test_upload_saves_file_to_upload_dir(upload_client, tmp_path):
    client, _, _ = upload_client

    client.post(
        "/upload/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert (tmp_path / "test.pdf").read_bytes() == b"pdf content"


def test_upload_processes_only_supported_files_in_batch(upload_client, tmp_path):
    client, mock_session, mock_redis = upload_client

    response = client.post(
        "/upload/",
        files=[
            ("files", ("doc.pdf", b"pdf content", "application/pdf")),
            ("files", ("notes.txt", b"text content", "text/plain")),
        ],
    )

    assert response.status_code == 200
    assert response.json() == {
        "files_being_processed": [
            {"filename": "doc.pdf", "status": "pending"},
            {
                "filename": "notes.txt",
                "status": "skipped",
                "error": "Content type not allowed",
            },
        ]
    }
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_redis.lpush.assert_called_once_with(
        "jobs:upload", json.dumps({"document_id": 1})
    )
    assert (tmp_path / "doc.pdf").read_bytes() == b"pdf content"
    assert not (tmp_path / "notes.txt").exists()


def test_upload_skips_duplicate_filename(upload_client, mocker):
    client, mock_session, mock_redis = upload_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = mocker.MagicMock()
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/upload/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "files_being_processed": [
            {
                "filename": "test.pdf",
                "status": "skipped",
                "error": "already exists",
            }
        ]
    }
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_redis.lpush.assert_not_called()
