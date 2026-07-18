from fastapi import APIRouter
from pydantic import Field
from sqlalchemy import select


from api.dependencies import SessionDep, UserDep
from db.models.document import Document
from db.models.user import UserPlan
from api.schemas.camel_model import CamelModel
from api.dependencies import S3ClientDep

router = APIRouter(prefix="/user", tags=["user"])


class UpdateUserRequest(CamelModel):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)


class UserResponse(CamelModel):
    id: int
    first_name: str
    last_name: str
    email: str
    plan: UserPlan


@router.patch("/me")
def update_user(
    request: UpdateUserRequest, user: UserDep, session: SessionDep
) -> UserResponse:
    user.first_name = request.first_name
    user.last_name = request.last_name
    session.commit()

    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        plan=user.plan,
    )


@router.delete("/me", status_code=204)
def delete_user(user: UserDep, session: SessionDep, s3_client: S3ClientDep):
    user_documents = session.scalars(
        select(Document).where(Document.user_id == user.id)
    ).all()

    objects_to_delete = [document.s3_content_key for document in user_documents] + [
        document.s3_thumbnail_key for document in user_documents
    ]

    session.delete(user)
    session.commit()

    try:
        if len(objects_to_delete) > 0:
            s3_client.delete_files(objects_to_delete)
    except Exception:
        pass
