from datetime import datetime, timedelta, timezone
from shared.settings import settings, Environment
import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from db.models.user import User
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import secrets
from shared.redis_client import get_redis_client
from fastapi.responses import Response
from api.schemas.camel_model import CamelModel
from db.models.user import UserPlan

security = HTTPBearer()

REDIS_REFRESH_TOKEN_KEY_PREFIX = "refresh:"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"

def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expires_in_minutes)
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def persist_refresh_token(refresh_token: str, user_id: int):
    redis_client = get_redis_client()
    redis_client.set(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}", user_id, ex=settings.refresh_token_expires_in_days * 24 * 60 * 60)

def clear_refresh_token(refresh_token: str):
    redis_client = get_redis_client()
    redis_client.delete(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}")

def get_refresh_token_user_id(refresh_token: str) -> int | None:
    redis_client = get_redis_client()
    user_id =redis_client.get(f"{REDIS_REFRESH_TOKEN_KEY_PREFIX}{refresh_token}")

    if user_id is None:
        return None
    
    return int(user_id)

def set_refresh_token_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.environment == Environment.PRODUCTION,
        samesite="lax",
        max_age=settings.refresh_token_expires_in_days * 24 * 60 * 60,
        path="/",
    )

    return response

def clear_refresh_token_cookie(response: Response):
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/")

class AuthResponse(CamelModel):
    id: int
    first_name: str
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
        email=user.email,
        plan=user.plan,
        access_token=create_access_token(user.id),
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id = int(user_id)
        user = session.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

