from db.models.document import Document
from tests.api.factories import uid


def test_delete_user_success(user_client, mocker):
    client, mock_session, mock_s3_client, user, mock_bedrock_client = user_client

    documents = [
        Document(
            id=uid(1),
            user_id=user.id,
            name="doc1.pdf",
            s3_content_key="1/content1",
            s3_thumbnail_key="1/thumb1",
            content_type="application/pdf",
            size_bytes=1000,
        ),
        Document(
            id=uid(2),
            user_id=user.id,
            name="doc2.pdf",
            s3_content_key="1/content2",
            s3_thumbnail_key="1/thumb2",
            content_type="application/pdf",
            size_bytes=2000,
        ),
    ]

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = documents
    mock_session.scalars.return_value = mock_scalars
    mocker.patch(
        "api.routers.user.settings.is_document_processing_v2_enabled",
        False,
    )

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        ["1/content1", "1/content2", "1/thumb1", "1/thumb2"]
    )
    mock_bedrock_client.delete_documents.assert_not_called()


def test_delete_user_no_documents(user_client, mocker):
    client, mock_session, mock_s3_client, user, mock_bedrock_client = user_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = []
    mock_session.scalars.return_value = mock_scalars

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with([])


def test_delete_user_s3_failure_does_not_raise(user_client, mocker):
    client, mock_session, mock_s3_client, user, _ = user_client

    documents = [
        Document(
            id=uid(1),
            user_id=user.id,
            name="doc1.pdf",
            s3_content_key="1/content1",
            s3_thumbnail_key="1/thumb1",
            content_type="application/pdf",
            size_bytes=1000,
        ),
    ]

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = documents
    mock_session.scalars.return_value = mock_scalars
    mock_s3_client.delete_files.side_effect = Exception("S3 failure")

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.commit.assert_called_once()


def test_delete_user_calls_bedrock_when_v2_enabled(user_client, mocker):
    client, mock_session, mock_s3_client, user, mock_bedrock_client = user_client

    documents = [
        Document(
            id=uid(1),
            user_id=user.id,
            name="doc1.pdf",
            s3_content_key="1/content1",
            s3_thumbnail_key="1/thumb1",
            content_type="application/pdf",
            size_bytes=1000,
        ),
        Document(
            id=uid(2),
            user_id=user.id,
            name="doc2.pdf",
            s3_content_key="1/content2",
            s3_thumbnail_key="1/thumb2",
            content_type="application/pdf",
            size_bytes=2000,
        ),
    ]

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = documents
    mock_session.scalars.return_value = mock_scalars
    mocker.patch(
        "api.routers.user.settings.is_document_processing_v2_enabled",
        True,
    )

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        ["1/content1", "1/content2", "1/thumb1", "1/thumb2"]
    )
    mock_bedrock_client.delete_documents.assert_called_once_with([uid(1), uid(2)])


def test_delete_user_bedrock_failure_does_not_raise(user_client, mocker):
    client, mock_session, mock_s3_client, user, mock_bedrock_client = user_client

    documents = [
        Document(
            id=uid(1),
            user_id=user.id,
            name="doc1.pdf",
            s3_content_key="1/content1",
            s3_thumbnail_key="1/thumb1",
            content_type="application/pdf",
            size_bytes=1000,
        ),
    ]

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = documents
    mock_session.scalars.return_value = mock_scalars
    mocker.patch(
        "api.routers.user.settings.is_document_processing_v2_enabled",
        True,
    )
    mock_bedrock_client.delete_documents.side_effect = Exception("Bedrock failure")

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once()
    mock_bedrock_client.delete_documents.assert_called_once_with([uid(1)])
