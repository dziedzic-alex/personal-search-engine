import zipfile
from io import BytesIO

from api.routers.documents.documents import MAX_BULK_DOWNLOAD_BYTE_SIZE
from tests.api.factories import make_document


def test_bulk_download_returns_zip_with_requested_documents(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client
    documents = [
        make_document(
            id=1,
            name="report.pdf",
            s3_content_key="1/report.pdf",
            size_bytes=100,
        ),
        make_document(
            id=2,
            name="notes.pdf",
            s3_content_key="1/notes.pdf",
            size_bytes=200,
        ),
    ]
    mock_session.scalars.return_value.all.return_value = documents
    mock_s3_client.get_file.side_effect = lambda key: f"content-of-{key}".encode()

    response = client.post(
        "/documents/bulk-download",
        json={"documentIds": [1, 2]},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    with zipfile.ZipFile(BytesIO(response.content)) as zf:
        assert sorted(zf.namelist()) == ["notes.pdf", "report.pdf"]
        assert zf.read("report.pdf") == b"content-of-1/report.pdf"
        assert zf.read("notes.pdf") == b"content-of-1/notes.pdf"


def test_bulk_download_returns_404_when_any_document_missing(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client
    mock_session.scalars.return_value.all.return_value = [
        make_document(id=1, size_bytes=100),
    ]

    response = client.post(
        "/documents/bulk-download",
        json={"documentIds": [1, 2]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "One or more documents not found"
    mock_s3_client.get_file.assert_not_called()


def test_bulk_download_returns_400_when_total_size_exceeds_limit(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client
    documents = [
        make_document(id=1, size_bytes=MAX_BULK_DOWNLOAD_BYTE_SIZE),
        make_document(id=2, name="notes.pdf", size_bytes=1),
    ]
    mock_session.scalars.return_value.all.return_value = documents

    response = client.post(
        "/documents/bulk-download",
        json={"documentIds": [1, 2]},
    )

    assert response.status_code == 400
    assert "exceeds 2GB" in response.json()["detail"]
    mock_s3_client.get_file.assert_not_called()


def test_bulk_download_rejects_single_document_id(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client

    response = client.post(
        "/documents/bulk-download",
        json={"documentIds": [1]},
    )

    assert response.status_code == 422
    mock_session.scalars.assert_not_called()
    mock_s3_client.get_file.assert_not_called()


def test_bulk_download_rejects_empty_document_ids(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client

    response = client.post(
        "/documents/bulk-download",
        json={"documentIds": []},
    )

    assert response.status_code == 422
    mock_session.scalars.assert_not_called()
    mock_s3_client.get_file.assert_not_called()
