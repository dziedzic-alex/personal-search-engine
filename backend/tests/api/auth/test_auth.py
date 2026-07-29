from argon2 import PasswordHasher

from api.routers.auth.auth_utils import (
    REDIS_REFRESH_TOKEN_KEY_PREFIX,
    REFRESH_TOKEN_COOKIE_NAME,
    parse_refresh_cookie,
)
from db.models.user import UserPlan
from tests.api.conftest import make_user

ph = PasswordHasher()

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
    assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is None
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

    refresh_cookie = response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    assert refresh_cookie is not None
    parsed = parse_refresh_cookie(refresh_cookie)
    assert parsed.user_id == user.id
    assert redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"][parsed.refresh_token] == b"1"


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
    assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is None
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
    redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"] = {old_refresh_token: b"1"}
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, f"{user.id}:{old_refresh_token}")
    mock_session.get.return_value = user

    response = client.post("/auth/refresh")

    assert response.status_code == 200
    assert response.json()["accessToken"]
    assert old_refresh_token not in redis_store.get(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}", {})

    new_refresh_cookie = response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    assert new_refresh_cookie is not None
    assert new_refresh_cookie != f"{user.id}:{old_refresh_token}"

    parsed = parse_refresh_cookie(new_refresh_cookie)
    assert parsed.user_id == user.id
    assert redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"][parsed.refresh_token] == b"1"


def test_refresh_no_cookie(auth_client):
    client, _, _, _ = auth_client

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "No refresh cookie provided"


def test_refresh_invalid_cookie_format(auth_client):
    client, _, _, _ = auth_client
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "invalid-token")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh cookie"


def test_refresh_invalid_token(auth_client):
    client, _, _, _ = auth_client
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "1:missing-token")

    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_refresh_user_not_found(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client

    refresh_token = "stale-refresh-token"
    redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}1"] = {refresh_token: b"1"}
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, f"1:{refresh_token}")
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
    refresh_cookie = login_response.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    assert refresh_cookie is not None
    parsed = parse_refresh_cookie(refresh_cookie)
    assert parsed.refresh_token in redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"]

    other_device_token = "other-device-token"
    redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"][other_device_token] = b"1"

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert parsed.refresh_token not in redis_store.get(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}", {})
    assert other_device_token in redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"]

    set_cookie = response.headers.get("set-cookie", "")
    assert REFRESH_TOKEN_COOKIE_NAME + "=" in set_cookie
    assert "Max-Age=0" in set_cookie


def test_logout_without_cookie(auth_client):
    client, _, redis_store, _ = auth_client

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert redis_store == {}


def test_logout_with_malformed_cookie_still_clears_cookie(auth_client):
    client, _, redis_store, _ = auth_client
    client.cookies.set(REFRESH_TOKEN_COOKIE_NAME, "not-a-valid-cookie")

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert redis_store == {}
    set_cookie = response.headers.get("set-cookie", "")
    assert REFRESH_TOKEN_COOKIE_NAME + "=" in set_cookie
    assert "Max-Age=0" in set_cookie


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
    assert response.cookies.get(REFRESH_TOKEN_COOKIE_NAME) is not None


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


def test_request_password_change_success(auth_client, mocker):
    client, mock_session, redis_store, mock_ses = auth_client
    user = make_user()

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = user
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/request-password-change",
        json={"email": "test@example.com"},
    )

    assert response.status_code == 204
    assert f"password_reset_token:{user.id}" in redis_store
    mock_ses.send_email.assert_called_once()
    send_kwargs = mock_ses.send_email.call_args.kwargs
    assert send_kwargs["to_addresses"] == ["test@example.com"]
    assert "http://localhost:5173/reset-password?token=" in send_kwargs["body"]
    assert f"user_id={user.id}" in send_kwargs["body"]


def test_request_password_change_unknown_user_is_opaque(auth_client, mocker):
    client, mock_session, redis_store, mock_ses = auth_client

    mock_scalars = mocker.MagicMock()
    mock_scalars.first.return_value = None
    mock_session.scalars.return_value = mock_scalars

    response = client.post(
        "/auth/request-password-change",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 204
    assert redis_store == {}
    mock_ses.send_email.assert_not_called()


def test_reset_password_success_revokes_sessions(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user()
    old_password_hash = user.password
    token = "valid-reset-token"

    redis_store[f"password_reset_token:{user.id}"] = token.encode()
    redis_store[f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}"] = {
        "session-a": b"1",
        "session-b": b"1",
    }
    mock_session.get.return_value = user

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "userId": user.id,
            "newPassword": "newpassword123",
        },
    )

    assert response.status_code == 204
    assert user.password != old_password_hash
    ph.verify(user.password, "newpassword123")
    mock_session.commit.assert_called()
    assert f"password_reset_token:{user.id}" not in redis_store
    assert f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{user.id}" not in redis_store


def test_reset_password_invalid_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client

    response = client.post(
        "/auth/reset-password",
        json={
            "token": "missing-token",
            "userId": 1,
            "newPassword": "newpassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password reset token"
    mock_session.get.assert_not_called()
    assert redis_store == {}


def test_reset_password_wrong_token(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    user = make_user()

    redis_store[f"password_reset_token:{user.id}"] = b"expected-token"

    response = client.post(
        "/auth/reset-password",
        json={
            "token": "wrong-token",
            "userId": user.id,
            "newPassword": "newpassword123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password reset token"
    mock_session.get.assert_not_called()
    assert f"password_reset_token:{user.id}" in redis_store


def test_reset_password_user_not_found(auth_client, mocker):
    client, mock_session, redis_store, _ = auth_client
    token = "valid-reset-token"

    redis_store["password_reset_token:1"] = token.encode()
    mock_session.get.return_value = None

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "userId": 1,
            "newPassword": "newpassword123",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User associated with token not found"
    assert "password_reset_token:1" in redis_store
