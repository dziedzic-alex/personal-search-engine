from sqlalchemy.sql.dml import Delete

from tests.api.factories import make_document, uid


def test_delete_document_removes_document_and_s3_objects(documents_client, mocker):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    document = make_document()
    mock_session.get.return_value = document
    mocker.patch(
        "api.routers.documents.documents.settings.is_document_processing_v2_enabled",
        False,
    )

    response = client.delete(f"/documents/{uid(1)}")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(document)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        ["1/report.pdf", "1/thumbnail_report.jpg"]
    )
    mock_bedrock_client.delete_documents.assert_not_called()


def test_delete_document_calls_bedrock_when_v2_enabled(documents_client, mocker):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    document = make_document()
    mock_session.get.return_value = document
    mocker.patch(
        "api.routers.documents.documents.settings.is_document_processing_v2_enabled",
        True,
    )

    response = client.delete(f"/documents/{uid(1)}")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(document)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        ["1/report.pdf", "1/thumbnail_report.jpg"]
    )
    mock_bedrock_client.delete_documents.assert_called_once_with([uid(1)])


def test_bulk_delete_documents_removes_documents_and_s3_objects(
    documents_client, mocker
):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    documents = [
        make_document(
            id=uid(1),
            s3_content_key="1/report.pdf",
            s3_thumbnail_key="1/thumbnail_report.jpg",
        ),
        make_document(
            id=uid(2),
            name="notes.pdf",
            s3_content_key="1/notes.pdf",
            s3_thumbnail_key="1/thumbnail_notes.jpg",
        ),
    ]
    mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=documents,
    )
    mocker.patch(
        "api.routers.documents.documents.settings.is_document_processing_v2_enabled",
        False,
    )

    response = client.request(
        "DELETE",
        "/documents/bulk-delete",
        json={"documentIds": [str(uid(1)), str(uid(2))]},
    )

    assert response.status_code == 204
    mock_session.execute.assert_called_once()
    assert isinstance(mock_session.execute.call_args[0][0], Delete)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        [
            "1/report.pdf",
            "1/notes.pdf",
            "1/thumbnail_report.jpg",
            "1/thumbnail_notes.jpg",
        ]
    )
    mock_bedrock_client.delete_documents.assert_not_called()


def test_bulk_delete_documents_calls_bedrock_when_v2_enabled(documents_client, mocker):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    documents = [
        make_document(
            id=uid(1),
            s3_content_key="1/report.pdf",
            s3_thumbnail_key="1/thumbnail_report.jpg",
        ),
        make_document(
            id=uid(2),
            name="notes.pdf",
            s3_content_key="1/notes.pdf",
            s3_thumbnail_key="1/thumbnail_notes.jpg",
        ),
    ]
    mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=documents,
    )
    mocker.patch(
        "api.routers.documents.documents.settings.is_document_processing_v2_enabled",
        True,
    )

    response = client.request(
        "DELETE",
        "/documents/bulk-delete",
        json={"documentIds": [str(uid(1)), str(uid(2))]},
    )

    assert response.status_code == 204
    mock_session.execute.assert_called_once()
    assert isinstance(mock_session.execute.call_args[0][0], Delete)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        [
            "1/report.pdf",
            "1/notes.pdf",
            "1/thumbnail_report.jpg",
            "1/thumbnail_notes.jpg",
        ]
    )
    mock_bedrock_client.delete_documents.assert_called_once_with([uid(1), uid(2)])


def test_bulk_delete_documents_returns_404_when_any_document_missing(
    documents_client,
    mocker,
):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client
    mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=[make_document(id=uid(1))],
    )

    response = client.request(
        "DELETE",
        "/documents/bulk-delete",
        json={"documentIds": [str(uid(1)), str(uid(2))]},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "One or more documents not found"
    mock_session.execute.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_s3_client.delete_files.assert_not_called()
    mock_bedrock_client.delete_documents.assert_not_called()


def test_bulk_delete_documents_rejects_empty_document_ids(documents_client):
    client, mock_session, _, _, mock_s3_client, mock_bedrock_client = documents_client

    response = client.request(
        "DELETE",
        "/documents/bulk-delete",
        json={"documentIds": []},
    )

    assert response.status_code == 422
    mock_session.execute.assert_not_called()
    mock_s3_client.delete_files.assert_not_called()
    mock_bedrock_client.delete_documents.assert_not_called()
