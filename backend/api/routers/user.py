import logging
import uuid

from fastapi import APIRouter
from pydantic import Field
from sqlalchemy import select

from api.dependencies import BedrockClientDep, S3ClientDep, SessionDep, UserDep
from api.schemas.camel_model import CamelModel
from db.models.document import Document
from db.models.user import UserPlan
from shared.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["user"])


class UpdateUserRequest(CamelModel):
    first_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)


class UserResponse(CamelModel):
    id: uuid.UUID
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
def delete_user(user: UserDep, session: SessionDep, s3_client: S3ClientDep, bedrock_client: BedrockClientDep):
    user_documents = session.scalars(
        select(Document).where(Document.user_id == user.id)
    ).all()

    objects_to_delete = [document.s3_content_key for document in user_documents] + [
        document.s3_thumbnail_key for document in user_documents
    ]

    session.delete(user)
    session.commit()

    try:
        s3_client.delete_files(objects_to_delete)
    except Exception:
        logger.error(f"Error deleting user {user.id} documents from S3", exc_info=True)
        pass

    if settings.is_document_processing_v2_enabled:
        try:
            bedrock_client.delete_documents([document.id for document in user_documents])
        except Exception:
            logger.error(f"Error deleting user {user.id} documents from Bedrock", exc_info=True)
            pass
