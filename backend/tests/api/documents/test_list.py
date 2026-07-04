from db.repositories.documents import DOCUMENT_LIST_PAGE_SIZE
from tests.api.factories import api_document_json, make_document


def test_list_documents_returns_user_documents(documents_client, mocker):
    client, _, _, _, _ = documents_client
    document = make_document()
    mock_get_documents = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents",
        return_value=[document],
    )

    response = client.post("/documents/list", json={"page": 0})

    assert response.status_code == 200
    assert response.json() == {
        "documents": [api_document_json(document)],
        "nextPage": None,
    }
    mock_get_documents.assert_called_once_with(1, None, None, None, 0)


def test_list_documents_returns_next_page_when_page_is_full(documents_client, mocker):
    client, _, _, _, _ = documents_client
    documents = [
        make_document(id=document_id, name=f"report-{document_id}.pdf")
        for document_id in range(1, DOCUMENT_LIST_PAGE_SIZE + 1)
    ]
    mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents",
        return_value=documents,
    )

    response = client.post("/documents/list", json={"page": 0})

    assert response.status_code == 200
    assert response.json() == {
        "documents": [api_document_json(document) for document in documents],
        "nextPage": 1,
    }


def test_list_documents_passes_query_sort_and_filter_config(documents_client, mocker):
    client, _, _, _, _ = documents_client
    mock_get_documents = mocker.patch(
        "api.routers.documents.documents.DocumentRepository.get_documents",
        return_value=[],
    )

    response = client.post(
        "/documents/list",
        json={
            "page": 2,
            "query": "report",
            "sortConfig": {"column": "name", "direction": "asc"},
            "filterConfig": {
                "type": "pdf",
                "status": "processed",
                "dateUploaded": "last7Days",
                "dateCreated": None,
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {"documents": [], "nextPage": None}

    call_args = mock_get_documents.call_args
    assert call_args.args[0] == 1
    assert call_args.args[1] == "report"
    assert call_args.args[2].column.value == "name"
    assert call_args.args[2].direction.value == "asc"
    assert call_args.args[3].type.value == "pdf"
    assert call_args.args[3].status.value == "processed"
    assert call_args.args[3].dateUploaded.value == "last7Days"
    assert call_args.args[3].dateCreated is None
    assert call_args.args[4] == 2
