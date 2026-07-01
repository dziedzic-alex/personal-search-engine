from tests.api.factories import make_document


def test_update_document_renames_document(documents_client):
    client, mock_session, _, _, _ = documents_client
    document = make_document()
    mock_session.get.return_value = document

    response = client.patch("/documents/1", json={"name": "annual report.pdf"})

    assert response.status_code == 200
    assert response.json()["name"] == "annual report.pdf"
    assert document.name == "annual report.pdf"
    mock_session.commit.assert_called_once()


def test_update_document_returns_404_when_missing(documents_client):
    client, mock_session, _, _, _ = documents_client
    mock_session.get.return_value = None

    response = client.patch("/documents/1", json={"name": "new.pdf"})

    assert response.status_code == 404


def test_update_document_returns_403_for_other_users_document(documents_client):
    client, mock_session, _, _, _ = documents_client
    mock_session.get.return_value = make_document(user_id=2)

    response = client.patch("/documents/1", json={"name": "new.pdf"})

    assert response.status_code == 403


def test_update_document_returns_409_when_name_already_exists(documents_client, mocker):
    client, mock_session, _, _, _ = documents_client
    document = make_document()
    mock_session.get.return_value = document

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = make_document(id=2, name="existing.pdf")
    mock_session.scalars.return_value = mock_scalars

    response = client.patch("/documents/1", json={"name": "existing.pdf"})

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Document with given name already exists",
    }
    assert document.name == "report.pdf"
    mock_session.commit.assert_not_called()
