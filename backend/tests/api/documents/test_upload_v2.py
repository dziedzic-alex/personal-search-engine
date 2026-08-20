from db.models.document import DocumentStatus
from shared.bedrock_client import BedrockClient
from shared.content_type import ContentType
from tests.api.factories import uid

FILE_GROUP_ID = "550e8400-e29b-41d4-a716-446655440000"
USER_ID = uid(1)
CONTENT_KEY = f"{USER_ID}/{FILE_GROUP_ID}/content"
THUMBNAIL_KEY = f"{USER_ID}/{FILE_GROUP_ID}/thumbnail"


def test_upload_v2_pdf_ingests_text_document(documents_client, mock_user):
    client, mock_session, mock_sqs_client, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )
    mock_bedrock_client.ingest_text_document.return_value = DocumentStatus.PENDING

    response = client.post(
        "/documents/v2",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(uid(1))
    assert payload["name"] == "test.pdf"
    assert payload["contentCategory"] == "pdf"
    assert payload["status"] == "pending"
    assert payload["size"] == len(b"pdf content")

    mock_persist_file_to_s3.assert_called_once()
    persist_args = mock_persist_file_to_s3.call_args[0]
    assert persist_args[1] == b"pdf content"
    assert persist_args[2] == mock_user.id
    assert persist_args[3] == ContentType.PDF

    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_bedrock_client.ingest_text_document.assert_called_once_with(
        uid(1), CONTENT_KEY, mock_user.id
    )
    mock_bedrock_client.ingest_image_document.assert_not_called()
    mock_sqs_client.submit_document_message.assert_not_called()


def test_upload_v2_image_ingests_image_document(documents_client, mock_user):
    client, mock_session, mock_sqs_client, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )
    image_bytes = b"jpeg-bytes"
    mock_bedrock_client.ingest_image_document.return_value = DocumentStatus.PENDING

    response = client.post(
        "/documents/v2",
        files={"file": ("photo.jpg", image_bytes, "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "photo.jpg"
    assert payload["contentCategory"] == "image"
    assert payload["size"] == len(image_bytes)

    mock_persist_file_to_s3.assert_called_once()
    persist_args = mock_persist_file_to_s3.call_args[0]
    assert persist_args[1] == image_bytes
    assert persist_args[3] == ContentType.JPEG

    mock_bedrock_client.ingest_image_document.assert_called_once_with(
        uid(1), mock_user.id, image_bytes, ContentType.JPEG
    )
    mock_bedrock_client.ingest_text_document.assert_not_called()
    mock_session.commit.assert_called_once()
    mock_sqs_client.submit_document_message.assert_not_called()


def test_upload_v2_converts_heic_to_jpeg_before_ingest(documents_client, mocker, mock_user):
    client, mock_session, _, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )
    jpeg_bytes = b"converted-jpeg"
    mocker.patch(
        "api.routers.documents.documents.convert_heic_or_heif_to_jpeg",
        return_value=jpeg_bytes,
    )
    mock_bedrock_client.ingest_image_document.return_value = DocumentStatus.PENDING

    response = client.post(
        "/documents/v2",
        files={"file": ("photo.heic", b"heic-bytes", "image/heic")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "photo.jpg"
    assert payload["contentCategory"] == "image"
    assert payload["size"] == len(jpeg_bytes)

    mock_persist_file_to_s3.assert_called_once()
    persist_args = mock_persist_file_to_s3.call_args[0]
    assert persist_args[1] == jpeg_bytes
    assert persist_args[3] == ContentType.JPEG
    mock_bedrock_client.ingest_image_document.assert_called_once_with(
        uid(1), mock_user.id, jpeg_bytes, ContentType.JPEG
    )


def test_upload_v2_rejects_image_over_bedrock_size_limit(documents_client, mocker):
    client, mock_session, _, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )
    too_large = (
        b"x" * (BedrockClient.MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES + 1)
    )

    response = client.post(
        "/documents/v2",
        files={"file": ("big.jpg", too_large, "image/jpeg")},
    )

    assert response.status_code == 413
    mock_persist_file_to_s3.assert_not_called()
    mock_session.add.assert_not_called()
    mock_bedrock_client.ingest_image_document.assert_not_called()


def test_upload_v2_duplicate_check_uses_converted_heic_filename(
    documents_client, mocker
):
    client, mock_session, _, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )
    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = mocker.MagicMock()
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/documents/v2",
        files={"file": ("photo.heic", b"heic-bytes", "image/heic")},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Document photo.jpg already exists"
    mock_persist_file_to_s3.assert_not_called()
    mock_bedrock_client.ingest_image_document.assert_not_called()


def test_upload_v2_returns_415_for_unsupported_content_type(documents_client):
    client, mock_session, _, mock_persist_file_to_s3, _, mock_bedrock_client = (
        documents_client
    )

    response = client.post(
        "/documents/v2",
        files={"file": ("notes.txt", b"text content", "text/plain")},
    )

    assert response.status_code == 415
    mock_persist_file_to_s3.assert_not_called()
    mock_session.add.assert_not_called()
    mock_bedrock_client.ingest_text_document.assert_not_called()


def test_upload_v2_rolls_back_s3_on_flush_failure(documents_client, mocker):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    mock_session.flush.side_effect = Exception("db error")

    response = client.post(
        "/documents/v2",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
    )

    assert response.status_code == 500
    mock_session.rollback.assert_called_once()
    mock_s3_client.delete_file.assert_any_call(CONTENT_KEY)
    mock_s3_client.delete_file.assert_any_call(THUMBNAIL_KEY)
    mock_bedrock_client.ingest_text_document.assert_not_called()
    mock_session.commit.assert_not_called()


def test_upload_v2_rolls_back_s3_and_db_on_ingest_failure(documents_client, mocker):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    mock_bedrock_client.ingest_text_document.side_effect = Exception("bedrock error")

    response = client.post(
        "/documents/v2",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
    )

    assert response.status_code == 500
    mock_session.rollback.assert_called_once()
    mock_s3_client.delete_file.assert_any_call(CONTENT_KEY)
    mock_s3_client.delete_file.assert_any_call(THUMBNAIL_KEY)
    mock_session.commit.assert_not_called()


def test_upload_v2_rolls_back_s3_db_and_bedrock_on_commit_failure(
    documents_client, mocker
):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    mock_bedrock_client.ingest_text_document.return_value = DocumentStatus.PENDING
    mock_session.commit.side_effect = Exception("commit error")

    response = client.post(
        "/documents/v2",
        files={"file": ("test.pdf", b"pdf content", "application/pdf")},
    )

    assert response.status_code == 500
    mock_session.rollback.assert_called_once()
    mock_s3_client.delete_file.assert_any_call(CONTENT_KEY)
    mock_s3_client.delete_file.assert_any_call(THUMBNAIL_KEY)
    mock_bedrock_client.delete_documents.assert_called_once_with([uid(1)])
