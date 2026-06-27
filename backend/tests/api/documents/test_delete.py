from tests.api.factories import make_document


def test_delete_document_removes_document_and_s3_objects(documents_client):
    client, mock_session, _, _, mock_s3_client = documents_client
    document = make_document()
    mock_session.get.return_value = document

    response = client.delete("/documents/1")

    assert response.status_code == 204
    mock_session.delete.assert_called_once_with(document)
    mock_session.commit.assert_called_once()
    mock_s3_client.delete_file.assert_any_call("1/report.pdf")
    mock_s3_client.delete_file.assert_any_call("1/thumbnail_report.jpg")
