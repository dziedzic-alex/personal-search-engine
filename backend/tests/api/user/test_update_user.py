def test_update_user_success(user_client):
    client, mock_session, _, user = user_client

    response = client.patch(
        "/user/me",
        json={"firstName": "Updated", "lastName": "Name"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "firstName": "Updated",
        "lastName": "Name",
        "email": user.email,
        "plan": "free",
    }
    assert user.first_name == "Updated"
    assert user.last_name == "Name"
    mock_session.commit.assert_called_once()


def test_update_user_empty_first_name(user_client):
    client, mock_session, _, _ = user_client

    response = client.patch(
        "/user/me",
        json={"firstName": "", "lastName": "Name"},
    )

    assert response.status_code == 422
    mock_session.commit.assert_not_called()


def test_update_user_empty_last_name(user_client):
    client, mock_session, _, _ = user_client

    response = client.patch(
        "/user/me",
        json={"firstName": "Test", "lastName": ""},
    )

    assert response.status_code == 422
    mock_session.commit.assert_not_called()


def test_update_user_first_name_too_long(user_client):
    client, mock_session, _, _ = user_client

    response = client.patch(
        "/user/me",
        json={"firstName": "a" * 256, "lastName": "Name"},
    )

    assert response.status_code == 422
    mock_session.commit.assert_not_called()


def test_update_user_last_name_too_long(user_client):
    client, mock_session, _, _ = user_client

    response = client.patch(
        "/user/me",
        json={"firstName": "Test", "lastName": "a" * 256},
    )

    assert response.status_code == 422
    mock_session.commit.assert_not_called()


def test_update_user_missing_fields(user_client):
    client, mock_session, _, _ = user_client

    response = client.patch("/user/me", json={})

    assert response.status_code == 422
    mock_session.commit.assert_not_called()
