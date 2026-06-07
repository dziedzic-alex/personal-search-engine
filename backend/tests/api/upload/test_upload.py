import json


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
        "files_being_processed": [{"filename": "doc.pdf", "status": "pending"}]
    }
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_redis.lpush.assert_called_once_with(
        "jobs:upload", json.dumps({"document_id": 1})
    )
    assert (tmp_path / "doc.pdf").read_bytes() == b"pdf content"
    assert not (tmp_path / "notes.txt").exists()
