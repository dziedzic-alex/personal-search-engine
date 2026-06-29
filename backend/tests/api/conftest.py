import pytest
from argon2 import PasswordHasher

from db.models.user import User, UserPlan

ph = PasswordHasher()


@pytest.fixture
def mock_s3_client(mocker):
    client = mocker.MagicMock()

    def generate_presigned_url(
        object_key, expires_in=3600, content_disposition_config=None
    ):
        return f"https://presigned.example/{object_key}"

    client.generate_presigned_url.side_effect = generate_presigned_url
    client.delete_file = mocker.MagicMock()
    return client


@pytest.fixture
def mock_user() -> User:
    return User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        password="hashed",
        plan=UserPlan.FREE,
    )


def make_user(**kwargs) -> User:
    defaults = {
        "id": 1,
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": ph.hash("password123"),
        "plan": UserPlan.FREE,
    }
    defaults.update(kwargs)
    return User(**defaults)
