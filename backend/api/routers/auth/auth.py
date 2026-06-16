from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.session import get_session
from db.models.user import User
from pydantic import EmailStr, Field
from typing import Annotated
from argon2 import PasswordHasher
from api.schemas.camel_model import CamelModel
from api.routers.auth.auth_utils import (
    get_refresh_token_user_id,
    clear_refresh_token,
    issue_auth_response,
    AuthResponse,
    clear_refresh_token_cookie,
)
from fastapi import Cookie
from fastapi.responses import Response


router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()

SessionDep = Annotated[Session, Depends(get_session)]


class SignupRequest(CamelModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


@router.post("/signup", status_code=201)
def signup(
    request: SignupRequest, response: Response, session: SessionDep
) -> AuthResponse:
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

        return issue_auth_response(user, response)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exists")


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
        raise HTTPException(status_code=401, detail="Invalid credentials")

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
