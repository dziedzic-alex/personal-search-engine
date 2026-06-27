import pytest
from argon2 import PasswordHasher

from db.models.user import User, UserPlan

ph = PasswordHasher()


@pytest.fixture
def mock_s3_client(mocker):
    client = mocker.MagicMock()
    client.generate_presigned_url.side_effect = lambda object_key, expires_in=3600: (
        f"https://presigned.example/{object_key}"
    )
    client.delete_file = mocker.MagicMock()
    client.get_file = mocker.MagicMock(return_value=b"")
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
