from types import SimpleNamespace


def test_search_returns_matching_documents(search_client, mocker):
    mock_results = [
        SimpleNamespace(name="photo.jpg", distance=0.15),
        SimpleNamespace(name="doc.pdf", distance=0.42),
    ]
    mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_documents",
        return_value=mock_results,
    )

    response = search_client.get("/search/", params={"query": "person eating a burger"})

    assert response.status_code == 200
    assert response.json() == [
        {"name": "photo.jpg", "distance": 0.15},
        {"name": "doc.pdf", "distance": 0.42},
    ]


def test_search_returns_empty_list_when_no_matches(search_client):
    response = search_client.get("/search/", params={"query": "nothing here"})

    assert response.status_code == 200
    assert response.json() == []
