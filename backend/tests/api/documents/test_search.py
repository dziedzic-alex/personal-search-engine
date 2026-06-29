from tests.api.factories import make_document


def test_text_search_returns_matching_documents(documents_client, mocker):
    client, _, _, _, _ = documents_client
    documents = [
        make_document(
            id=1,
            name="alex dziedzic PIIA.pdf",
            s3_content_key="1/piia.pdf",
            s3_thumbnail_key="1/thumbnail_piia.jpg",
        ),
        make_document(
            id=2,
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
    assert response.json() == [
        {
            "id": 1,
            "name": "alex dziedzic PIIA.pdf",
            "contentCategory": "pdf",
            "status": "processed",
            "numAttempts": 0,
            "previewUrl": "https://presigned.example/1/piia.pdf",
            "downloadUrl": "https://presigned.example/1/piia.pdf",
            "thumbnailUrl": "https://presigned.example/1/thumbnail_piia.jpg",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": documents[0].created_time.isoformat(),
        },
        {
            "id": 2,
            "name": "Nutshell Exit Agreement - Alex Dziedzic (2).pdf",
            "contentCategory": "pdf",
            "status": "processed",
            "numAttempts": 0,
            "previewUrl": "https://presigned.example/1/exit.pdf",
            "downloadUrl": "https://presigned.example/1/exit.pdf",
            "thumbnailUrl": "https://presigned.example/1/thumbnail_exit.jpg",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": documents[1].created_time.isoformat(),
        },
    ]
    mock_get_text.assert_called_once_with("laid off", 1)


def test_image_search_returns_matching_documents(documents_client, mocker):
    client, _, _, _, _ = documents_client
    documents = [
        make_document(
            id=1,
            name="photo.jpg",
            content_type="jpeg",
            s3_content_key="1/photo.jpg",
            s3_thumbnail_key="1/thumbnail_photo.jpg",
        ),
        make_document(
            id=2,
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
    assert response.json() == [
        {
            "id": 1,
            "name": "photo.jpg",
            "contentCategory": "image",
            "status": "processed",
            "numAttempts": 0,
            "previewUrl": "https://presigned.example/1/photo.jpg",
            "downloadUrl": "https://presigned.example/1/photo.jpg",
            "thumbnailUrl": "https://presigned.example/1/thumbnail_photo.jpg",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": documents[0].created_time.isoformat(),
        },
        {
            "id": 2,
            "name": "scan.png",
            "contentCategory": "image",
            "status": "processed",
            "numAttempts": 0,
            "previewUrl": "https://presigned.example/1/scan.png",
            "downloadUrl": "https://presigned.example/1/scan.png",
            "thumbnailUrl": "https://presigned.example/1/thumbnail_scan.png",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": documents[1].created_time.isoformat(),
        },
    ]
    mock_get_image.assert_called_once_with("person eating a burger", 1)


def test_search_returns_empty_list_when_no_matches(documents_client, mocker):
    client, _, _, _, _ = documents_client
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
