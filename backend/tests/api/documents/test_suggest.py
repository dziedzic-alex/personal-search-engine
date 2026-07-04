from tests.api.factories import api_document_json, make_document


def test_suggest_documents_returns_matching_documents(documents_client, mocker):
    client, _, _, _, _ = documents_client
    document = make_document(name="report.pdf")
    mock_suggest_documents = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.suggest_documents",
        return_value=[document],
    )

    response = client.get("/documents/suggest", params={"query": "rep"})

    assert response.status_code == 200
    assert response.json() == [api_document_json(document)]
    mock_suggest_documents.assert_called_once_with(1, "rep")
