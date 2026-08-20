from tests.api.factories import api_document_json, make_document, uid


def test_get_documents_by_ids_returns_documents(documents_client, mocker):
    client, _, _, _, _, _ = documents_client
    documents = [
        make_document(id=uid(1), name="report.pdf"),
        make_document(id=uid(2), name="photo.jpg", content_type="jpeg"),
    ]
    mock_get_documents_by_ids = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=documents,
    )

    response = client.post(
        "/documents/by-ids",
        json={"documentIds": [str(uid(1)), str(uid(2))]},
    )

    assert response.status_code == 200
    assert response.json() == [api_document_json(document) for document in documents]
    mock_get_documents_by_ids.assert_called_once_with([uid(1), uid(2)], uid(1))


def test_get_documents_by_ids_rejects_empty_document_ids(documents_client, mocker):
    client, _, _, _, _, _ = documents_client
    mock_get_documents_by_ids = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
    )

    response = client.post("/documents/by-ids", json={"documentIds": []})

    assert response.status_code == 422
    mock_get_documents_by_ids.assert_not_called()
