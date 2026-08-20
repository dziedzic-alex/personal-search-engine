from shared.bedrock_client import BedrockClient
from tests.api.factories import api_document_json, make_document, uid


def test_text_search_returns_matching_documents(documents_client, mocker):
    client, _, _, _, _, _ = documents_client
    documents = [
        make_document(
            id=uid(1),
            name="alex dziedzic PIIA.pdf",
            s3_content_key="1/piia.pdf",
            s3_thumbnail_key="1/thumbnail_piia.jpg",
        ),
        make_document(
            id=uid(2),
            name="Nutshell Exit Agreement - Alex Dziedzic (2).pdf",
            s3_content_key="1/exit.pdf",
            s3_thumbnail_key="1/thumbnail_exit.jpg",
        ),
    ]
    mock_get_text = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_relevant_text_documents",
        return_value=documents,
    )

    response = client.get(
        "/documents/search",
        params={"query": "laid off", "search_mode": "text"},
    )

    assert response.status_code == 200
    assert response.json() == [api_document_json(document) for document in documents]
    mock_get_text.assert_called_once_with("laid off", uid(1))


def test_image_search_returns_matching_documents(documents_client, mocker):
    client, _, _, _, _, _ = documents_client
    documents = [
        make_document(
            id=uid(1),
            name="photo.jpg",
            content_type="jpeg",
            s3_content_key="1/photo.jpg",
            s3_thumbnail_key="1/thumbnail_photo.jpg",
        ),
        make_document(
            id=uid(2),
            name="scan.png",
            content_type="png",
            s3_content_key="1/scan.png",
            s3_thumbnail_key="1/thumbnail_scan.png",
        ),
    ]
    mock_get_image = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_relevant_image_documents",
        return_value=documents,
    )

    response = client.get(
        "/documents/search",
        params={"query": "person eating a burger", "search_mode": "image"},
    )

    assert response.status_code == 200
    assert response.json() == [api_document_json(document) for document in documents]
    mock_get_image.assert_called_once_with("person eating a burger", uid(1))


def test_search_returns_empty_list_when_no_matches(documents_client, mocker):
    client, _, _, _, _, _ = documents_client
    mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_relevant_text_documents",
        return_value=[],
    )

    response = client.get(
        "/documents/search",
        params={"query": "nothing here", "search_mode": "text"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_search_v2_returns_documents_in_bedrock_order(documents_client, mocker, mock_user):
    client, _, _, _, _, mock_bedrock_client = documents_client
    documents = [
        make_document(id=uid(1), name="first.pdf"),
        make_document(id=uid(2), name="second.pdf"),
    ]
    mock_bedrock_client.retrieve_relevant_document_chunks.return_value = [
        BedrockClient.RelevantDocumentChunk(document_id=uid(2), score=0.9),
        BedrockClient.RelevantDocumentChunk(document_id=uid(1), score=0.7),
    ]
    mock_get_documents_by_ids = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=documents,
    )

    response = client.get("/documents/search/v2", params={"query": "laid off"})

    assert response.status_code == 200
    assert response.json() == [
        api_document_json(documents[1]),
        api_document_json(documents[0]),
    ]
    mock_bedrock_client.retrieve_relevant_document_chunks.assert_called_once_with(
        "laid off",
        mock_user.email,
    )
    mock_get_documents_by_ids.assert_called_once_with([uid(2), uid(1)], uid(1))


def test_search_v2_deduplicates_document_ids(documents_client, mocker):
    client, _, _, _, _, mock_bedrock_client = documents_client
    documents = [
        make_document(id=uid(1), name="report.pdf"),
        make_document(id=uid(2), name="contract.pdf"),
    ]
    mock_bedrock_client.retrieve_relevant_document_chunks.return_value = [
        BedrockClient.RelevantDocumentChunk(document_id=uid(1), score=0.9),
        BedrockClient.RelevantDocumentChunk(document_id=uid(1), score=0.8),
        BedrockClient.RelevantDocumentChunk(document_id=uid(2), score=0.6),
    ]
    mock_get_documents_by_ids = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=documents,
    )

    response = client.get("/documents/search/v2", params={"query": "contract"})

    assert response.status_code == 200
    assert response.json() == [api_document_json(document) for document in documents]
    mock_get_documents_by_ids.assert_called_once_with([uid(1), uid(2)], uid(1))


def test_search_v2_returns_empty_list_when_no_chunks(documents_client, mocker):
    client, _, _, _, _, mock_bedrock_client = documents_client
    mock_bedrock_client.retrieve_relevant_document_chunks.return_value = []
    mock_get_documents_by_ids = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents_by_ids",
        return_value=[],
    )

    response = client.get("/documents/search/v2", params={"query": "nothing"})

    assert response.status_code == 200
    assert response.json() == []
    mock_get_documents_by_ids.assert_called_once_with([], uid(1))
