from shared.content_type import ContentType

FILE_GROUP_ID = "550e8400-e29b-41d4-a716-446655440000"
CONTENT_KEY = f"1/{FILE_GROUP_ID}/content"
THUMBNAIL_KEY = f"1/{FILE_GROUP_ID}/thumbnail"


def test_upload_returns_files_being_processed(documents_client, mock_user):
    client, mock_session, mock_sqs_client, mock_persist_file, _ = documents_client

    response = client.post(
        "/documents/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["errors"] == []
    assert len(payload["filesBeingProcessed"]) == 1

    uploaded = payload["filesBeingProcessed"][0]
    assert uploaded["id"] == 1
    assert uploaded["name"] == "test.pdf"
    assert uploaded["contentCategory"] == "pdf"
    assert uploaded["status"] == "pending"
    assert uploaded["size"] == len(b"pdf content")
    assert uploaded["previewUrl"] == f"https://presigned.example/{CONTENT_KEY}"
    assert uploaded["downloadUrl"] == f"https://presigned.example/{CONTENT_KEY}"
    assert uploaded["thumbnailUrl"] == f"https://presigned.example/{THUMBNAIL_KEY}"
    assert uploaded["sourceCreatedTime"] is None
    assert "uploadedTime" in uploaded

    mock_persist_file.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_sqs_client.submit_document_message.assert_called_once_with(1, mock_user.id)


def test_upload_persists_files_to_s3(documents_client, mock_user):
    client, _, _, mock_persist_file, _ = documents_client

    client.post(
        "/documents/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    args = mock_persist_file.call_args[0]
    assert args[1] == b"pdf content"
    assert args[2] == mock_user.id
    assert args[3] == ContentType.PDF


def test_upload_processes_only_supported_files_in_batch(documents_client, mock_user):
    client, mock_session, mock_sqs_client, mock_persist_file, _ = documents_client

    response = client.post(
        "/documents/",
        files=[
            ("files", ("doc.pdf", b"pdf content", "application/pdf")),
            ("files", ("notes.txt", b"text content", "text/plain")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["errors"] == ["Content type text/plain not allowed"]
    assert len(payload["filesBeingProcessed"]) == 1
    assert payload["filesBeingProcessed"][0]["name"] == "doc.pdf"
    assert payload["filesBeingProcessed"][0]["status"] == "pending"

    mock_persist_file.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_sqs_client.submit_document_message.assert_called_once_with(1, mock_user.id)


def test_upload_skips_duplicate_filename(documents_client, mocker):
    client, mock_session, mock_sqs_client, mock_persist_file, _ = documents_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = mocker.MagicMock()
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/documents/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "filesBeingProcessed": [],
        "errors": ["Document test.pdf already exists"],
    }
    mock_persist_file.assert_not_called()
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_sqs_client.submit_document_message.assert_not_called()


def test_upload_rolls_back_s3_on_db_failure(documents_client, mocker):
    client, mock_session, mock_sqs_client, mock_persist_file, mock_s3_client = (
        documents_client
    )
    mock_session.commit.side_effect = Exception("db error")

    response = client.post(
        "/documents/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "filesBeingProcessed": [],
        "errors": ["Error saving document test.pdf"],
    }
    mock_session.rollback.assert_called_once()
    mock_s3_client.delete_file.assert_any_call(CONTENT_KEY)
    mock_s3_client.delete_file.assert_any_call(THUMBNAIL_KEY)
    mock_sqs_client.submit_document_message.assert_not_called()


def test_upload_rolls_back_db_and_s3_on_sqs_failure(documents_client, mock_s3_client):
    client, mock_session, mock_sqs_client, _, _ = documents_client
    mock_sqs_client.submit_document_message.side_effect = Exception("sqs error")

    response = client.post(
        "/documents/",
        files=[("files", ("test.pdf", b"pdf content", "application/pdf"))],
    )

    assert response.status_code == 200
    assert response.json() == {
        "filesBeingProcessed": [],
        "errors": ["Error submitting document test.pdf for processing"],
    }
    assert mock_session.commit.call_count == 2
    mock_session.delete.assert_called_once()
    mock_s3_client.delete_file.assert_any_call(CONTENT_KEY)
    mock_s3_client.delete_file.assert_any_call(THUMBNAIL_KEY)
    mock_sqs_client.submit_document_message.assert_called_once_with(1, 1)
