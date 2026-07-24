from db.models.user import UserPlan
from tests.api.conftest import make_user

SIGNUP_PAYLOAD = {
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "password": "password123",
}


def test_signup_success(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = None
    mock_session.scalars.return_value = mock_scalars

    def assign_user_fields(user):
        user.id = 1
        if user.plan is None:
            user.plan = UserPlan.FREE

    mock_session.add.side_effect = assign_user_fields

    response = client.post("/auth/signup", json=SIGNUP_PAYLOAD)

    assert response.status_code == 201
    assert response.json() == "test@example.com"
    assert response.cookies.get("refresh_token") is None
    assert redis_store == {}
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


def test_signup_duplicate_email(auth_client, mocker):
    client, mock_session, _, _ = auth_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = mocker.MagicMock()
    mock_session.scalars.return_value = mock_scalars

    response = client.post("/auth/signup", json=SIGNUP_PAYLOAD)

    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"
    mock_session.add.assert_not_called()


def test_login_success(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user()

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["accessToken"]

    refresh_token = response.cookies.get("refresh_token")
    assert refresh_token is not None
    assert redis_store[f"refresh:{refresh_token}"] == b"1"


def test_login_email_not_verified(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user(email_verified=False)

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Email not verified"
    assert response.cookies.get("refresh_token") is None
    assert redis_store == {}


def test_login_unknown_user(auth_client, mocker):
    client, mock_session, _, _ = auth_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = None
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_password(auth_client, mocker):
    client, mock_session, _, _ = auth_client
    user = make_user()

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_success_rotates_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user()

    old_refresh_token = "old-refresh-token"
    redis_store[f"refresh:{old_refresh_token}"] = b"1"
    client.cookies.set("refresh_token", old_refresh_token)
    mock_session.get.return_value = user

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["accessToken"]
    assert f"refresh:{old_refresh_token}" not in redis_store

    new_refresh_token = response.cookies.get("refresh_token")
    assert new_refresh_token is not None
    assert new_refresh_token != old_refresh_token
    assert redis_store[f"refresh:{new_refresh_token}"] == b"1"


def test_refresh_no_cookie(auth_client):
    client, _, _, _ = auth_client

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "No refresh token provided"


def test_refresh_invalid_token(auth_client):
    client, _, _, _ = auth_client
    client.cookies.set("refresh_token", "invalid-token")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_refresh_user_not_found(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client

    refresh_token = "stale-refresh-token"
    redis_store[f"refresh:{refresh_token}"] = b"999"
    client.cookies.set("refresh_token", refresh_token)
    mock_session.get.return_value = None

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert (
        response.json()["detail"] == "User associated with the refresh token not found"
    )


def test_logout_revokes_refresh_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user()

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    login_response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    refresh_token = login_response.cookies.get("refresh_token")
    assert refresh_token is not None
    assert f"refresh:{refresh_token}" in redis_store

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert f"refresh:{refresh_token}" not in redis_store

    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie
    assert "Max-Age=0" in set_cookie


def test_logout_without_cookie(auth_client):
    client, _, redis_store, _ = auth_client

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert redis_store == {}


def test_send_verification_email_success(auth_client, mocker):
    client, mock_session, redis_store, mock_ses = auth_client
    user = make_user(email_verified=False)

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/send-verification-email",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 204
    assert f"email_verification_token:{user.id}" in redis_store
    mock_ses.send_email.assert_called_once()
    send_kwargs = mock_ses.send_email.call_args.kwargs
    assert send_kwargs["to_addresses"] == ["test@example.com"]
    assert "http://localhost:5173/verify-email/confirm?token=" in send_kwargs["body"]
    assert f"user_id={user.id}" in send_kwargs["body"]


def test_send_verification_email_unknown_user_is_opaque(auth_client, mocker):
    client, mock_session, redis_store, mock_ses = auth_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = None
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/send-verification-email",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 204
    assert redis_store == {}
    mock_ses.send_email.assert_not_called()


def test_send_verification_email_already_verified_is_opaque(auth_client, mocker):
    client, mock_session, redis_store, mock_ses = auth_client
    user = make_user(email_verified=True)

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/send-verification-email",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 204
    assert redis_store == {}
    mock_ses.send_email.assert_not_called()


def test_verify_email_success(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user(email_verified=False)
    token = "valid-verification-token"

    redis_store[f"email_verification_token:{user.id}"] = token.encode()
    mock_session.get.return_value = user

    response = client.post(
        "/auth/verify-email",
        json={"token": token, "userId": user.id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["accessToken"]
    assert user.email_verified is True
    mock_session.commit.assert_called()
    assert f"email_verification_token:{user.id}" not in redis_store
    assert response.cookies.get("refresh_token") is not None


def test_verify_email_invalid_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client

    response = client.post(
        "/auth/verify-email",
        json={"token": "missing-token", "userId": 1},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"
    mock_session.get.assert_not_called()
    assert redis_store == {}


def test_verify_email_wrong_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user(email_verified=False)

    redis_store[f"email_verification_token:{user.id}"] = b"expected-token"

    response = client.post(
        "/auth/verify-email",
        json={"token": "wrong-token", "userId": user.id},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired verification token"
    mock_session.get.assert_not_called()
    assert f"email_verification_token:{user.id}" in redis_store


def test_verify_email_user_not_found(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    token = "valid-verification-token"

    redis_store["email_verification_token:1"] = token.encode()
    mock_session.get.return_value = None

    response = client.post(
        "/auth/verify-email",
        json={"token": token, "userId": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User associated with token not found"
    assert "email_verification_token:1" in redis_store
