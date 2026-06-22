from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers import search
from db.repositories.documents import SearchResult


def test_search_requires_auth():
    app = FastAPI()
    app.include_router(search.router)

    client = TestClient(app)
    response = client.get(
        "/search/",
        params={"query": "test", "search_mode": "text"},
    )

    assert response.status_code == 401


def test_text_search_returns_matching_documents(search_client, mocker):
    mock_results = [
        SearchResult(
            name="alex dziedzic PIIA.pdf",
            content_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/piia.pdf",
            thumbnail_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/thumbnail_piia.jpg",
            average_distance=0.502,
            cross_encoding_score=0.00103,
        ),
        SearchResult(
            name="Nutshell Exit Agreement - Alex Dziedzic (2).pdf",
            content_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/exit.pdf",
            thumbnail_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/thumbnail_exit.jpg",
            average_distance=0.477,
            cross_encoding_score=0.00026,
        ),
    ]
    mock_get_text = mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_text_documents",
        return_value=mock_results,
    )

    response = search_client.get(
        "/search/",
        params={"query": "laid off", "search_mode": "text"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "alex dziedzic PIIA.pdf",
            "distance": 0.502,
            "cross_encoding_score": 0.00103,
        },
        {
            "name": "Nutshell Exit Agreement - Alex Dziedzic (2).pdf",
            "distance": 0.477,
            "cross_encoding_score": 0.00026,
        },
    ]
    mock_get_text.assert_called_once_with("laid off", 1)


def test_image_search_returns_matching_documents(search_client, mocker):
    mock_results = [
        SearchResult(
            name="photo.jpg",
            content_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/photo.jpg",
            thumbnail_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/thumbnail_photo.jpg",
            average_distance=0.15,
            cross_encoding_score=None,
        ),
        SearchResult(
            name="scan.png",
            content_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/scan.png",
            thumbnail_url="https://s3.amazonaws.com/files-thumbnails-bucket/1/thumbnail_scan.png",
            average_distance=0.42,
            cross_encoding_score=0.0008,
        ),
    ]
    mock_get_image = mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_image_documents",
        return_value=mock_results,
    )

    response = search_client.get(
        "/search/",
        params={"query": "person eating a burger", "search_mode": "image"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "photo.jpg",
            "distance": 0.15,
            "cross_encoding_score": None,
        },
        {
            "name": "scan.png",
            "distance": 0.42,
            "cross_encoding_score": 0.0008,
        },
    ]
    mock_get_image.assert_called_once_with("person eating a burger", 1)


def test_search_returns_empty_list_when_no_matches(search_client):
    response = search_client.get(
        "/search/",
        params={"query": "nothing here", "search_mode": "text"},
    )

    assert response.status_code == 200
    assert response.json() == []
