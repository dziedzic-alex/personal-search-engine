from secrets import token_urlsafe

from argon2 import PasswordHasher
from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import Response
from pydantic import EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from api.dependencies import SessionDep
from api.dependencies.ses import SESClientDep
from api.routers.auth.auth_utils import (
    AuthResponse,
    clear_refresh_token,
    clear_refresh_token_cookie,
    get_refresh_token_user_id,
    issue_auth_response,
)
from api.schemas.camel_model import CamelModel
from db.models.user import User
from shared.redis_client import get_redis_client
from shared.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()


class SignupRequest(CamelModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


@router.post("/signup", status_code=201)
def signup(request: SignupRequest, session: SessionDep) -> str:
    sanitized_email = request.email.strip().lower()
    existing_user = session.scalars(
        select(User).where(User.email == sanitized_email)
    ).first()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="User already exists")

    try:
        hashed_password = ph.hash(request.password)

        user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=sanitized_email,
            password=hashed_password,
        )
        session.add(user)
        session.commit()

        return sanitized_email
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exists") from None


class LoginRequest(CamelModel):
    email: EmailStr
    password: str


@router.post("/login", status_code=200)
def login(
    request: LoginRequest, response: Response, session: SessionDep
) -> AuthResponse:
    sanitized_email = request.email.strip().lower()

    user = session.scalars(select(User).where(User.email == sanitized_email)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        ph.verify(user.password, request.password)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials") from None

    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    return issue_auth_response(user, response)


@router.post("/refresh")
def refresh(
    response: Response,
    session: SessionDep,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
) -> AuthResponse:
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="No refresh token provided")

    refresh_token_user_id = get_refresh_token_user_id(refresh_token)
    if refresh_token_user_id is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    clear_refresh_token(refresh_token)

    user = session.get(User, refresh_token_user_id)
    if user is None:
        clear_refresh_token_cookie(response)
        raise HTTPException(
            status_code=401, detail="User associated with the refresh token not found"
        )

    return issue_auth_response(user, response)


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
):
    if refresh_token is None:
        return

    clear_refresh_token(refresh_token)

    clear_refresh_token_cookie(response)


REDIS_EMAIL_VERIFICATION_TOKEN_KEY_PREFIX = "email_verification_token:"
EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES = 10


class SendVerificationEmailRequest(CamelModel):
    email: EmailStr


@router.post("/send-verification-email", status_code=204)
def send_verification_email(
    request: SendVerificationEmailRequest, session: SessionDep, ses: SESClientDep
):
    sanitized_email = request.email.strip().lower()
    user = session.scalars(select(User).where(User.email == sanitized_email)).first()
    if user is None or user.email_verified:
        return

    email_verification_token = token_urlsafe(32)
    redis_client = get_redis_client()
    redis_client.set(
        f"{REDIS_EMAIL_VERIFICATION_TOKEN_KEY_PREFIX}{user.id}",
        email_verification_token,
        ex=EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES * 60,
    )

    url = f"{settings.frontend_base_url}/verify-email/confirm?token={email_verification_token}&user_id={user.id}"

    ses.send_email(
        subject="Verify your email",
        body=f"Please navigate to the following URL to verify your email: {url}\n The link will expire in {EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES} minutes",
        html_body=f"<p>Click the following link to verify your email: <a href='{url}'>{url}</a></p><p>The link will expire in {EMAIL_VERIFICATION_TOKEN_EXPIRES_IN_MINUTES} minutes</p>",
        to_addresses=[sanitized_email],
    )


class VerifyEmailRequest(CamelModel):
    token: str = Field(min_length=1)
    user_id: int


@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest, session: SessionDep, response: Response
) -> AuthResponse:
    redis_client = get_redis_client()
    email_verification_token = redis_client.get(
        f"{REDIS_EMAIL_VERIFICATION_TOKEN_KEY_PREFIX}{request.user_id}"
    )

    if email_verification_token is None:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    if email_verification_token.decode() != request.token:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    user_id = int(request.user_id)
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail="User associated with token not found"
        )

    user.email_verified = True
    session.commit()

    redis_client.delete(f"{REDIS_EMAIL_VERIFICATION_TOKEN_KEY_PREFIX}{request.user_id}")

    return issue_auth_response(user, response)
