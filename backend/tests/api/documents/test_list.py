from tests.api.factories import make_document


def test_list_documents_returns_user_documents(documents_client, mocker):
    client, mock_session, _, _, _ = documents_client
    document = make_document()

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = [document]
    mock_session.scalars.return_value = mock_scalars

    response = client.get("/documents/list")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "report.pdf",
            "contentCategory": "pdf",
            "status": "processed",
            "numAttempts": 0,
            "previewUrl": "https://presigned.example/1/report.pdf",
            "downloadUrl": "https://presigned.example/1/report.pdf",
            "thumbnailUrl": "https://presigned.example/1/thumbnail_report.jpg",
            "size": 1024,
            "sourceCreatedTime": None,
            "uploadedTime": document.created_time.isoformat(),
        }
    ]
