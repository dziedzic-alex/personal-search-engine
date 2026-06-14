from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.session import get_session
from db.models import User
from pydantic import EmailStr, Field
from typing import Annotated
from argon2 import PasswordHasher
from api.schemas.camel_model import CamelModel

router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()

SessionDep = Annotated[Session, Depends(get_session)]

class SignupRequest(CamelModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)

@router.post("/signup", status_code=201)
def signup(request: SignupRequest, session: SessionDep):
    sanitized_email = request.email.strip().lower()
    existing_user = session.scalars(select(User).where(User.email == sanitized_email)).first()
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
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="User already exists")



    
