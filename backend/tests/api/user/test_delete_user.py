from db.models.document import Document


def test_delete_user_success(user_client, mocker):
    client, mock_session, mock_s3_client, user = user_client

    documents = [
        Document(
            id=1,
            user_id=user.id,
            name="doc1.pdf",
            s3_content_key="1/content1",
            s3_thumbnail_key="1/thumb1",
            content_type="application/pdf",
            size_bytes=1000,
        ),
        Document(
            id=2,
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

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_called_once_with(
        ["1/content1", "1/content2", "1/thumb1", "1/thumb2"]
    )


def test_delete_user_no_documents(user_client, mocker):
    client, mock_session, mock_s3_client, user = user_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.all.return_value = []
    mock_session.scalars.return_value = mock_scalars

    response = client.delete("/user/me")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_files.assert_not_called()


def test_delete_user_s3_failure_does_not_raise(user_client, mocker):
    client, mock_session, mock_s3_client, user = user_client

    documents = [
        Document(
            id=1,
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
