import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.responses import Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies.db import SessionDep
from api.schemas.camel_model import CamelModel
from db.models.user import User, UserPlan
from shared.redis_client import get_redis_client
from shared.settings import Environment, settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_IN_MINUTES = 10
REFRESH_TOKEN_EXPIRES_IN_DAYS = 7

REDIS_REFRESH_TOKEN_KEY_PREFIX = "refresh:"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


def create_access_token(user_id: int):
    now = datetime.now(UTC)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN_MINUTES),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def persist_refresh_token(refresh_token: str, user_id: int):
    redis_client = get_redis_client()
    redis_client.set(
        f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}",
        user_id,
        ex=REFRESH_TOKEN_EXPIRES_IN_DAYS * 24 * 60 * 60,
    )


def clear_refresh_token(refresh_token: str):
    redis_client = get_redis_client()
    redis_client.delete(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}")


def get_refresh_token_user_id(refresh_token: str) -> int | None:
    redis_client = get_redis_client()
    user_id = redis_client.get(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}")

    if user_id is None:
        return None

    return int(user_id)


def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.environment == Environment.PROD,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRES_IN_DAYS * 24 * 60 * 60,
        path="/",
    )

    return response


def clear_refresh_token_cookie(response: Response):
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/")


class AuthResponse(CamelModel):
    id: int
    first_name: str
    last_name: str
    email: str
    plan: UserPlan
    access_token: str


def issue_auth_response(user: User, response: Response) -> AuthResponse:
    refresh_token = create_refresh_token()
    persist_refresh_token(refresh_token, user.id)

    set_refresh_token_cookie(response, refresh_token)

    return AuthResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        plan=user.plan,
        access_token=create_access_token(user.id),
    )


security = HTTPBearer()
SecurityDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


def get_current_user(
    credentials: SecurityDep,
    session: SessionDep,
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[JWT_ALGORITHM],
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = int(user_id)
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
