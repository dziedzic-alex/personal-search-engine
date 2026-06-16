import enum
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.routers.auth.auth_utils import get_current_user
from db.models import User
from db.repositories.documents import DocumentRepository
from db.session import get_session

router = APIRouter(prefix="/search", tags=["search"])

SessionDep = Annotated[Session, Depends(get_session)]
UserDep = Annotated[User, Depends(get_current_user)]


class SearchMode(enum.StrEnum):
    TEXT = "text"
    IMAGE = "image"


@router.get("/")
def search(query: str, search_mode: SearchMode, session: SessionDep, user: UserDep):
    if search_mode == SearchMode.TEXT:
        relevant_documents = DocumentRepository(session).get_relevant_text_documents(
            query, user.id
        )
    elif search_mode == SearchMode.IMAGE:
        relevant_documents = DocumentRepository(session).get_relevant_image_documents(
            query, user.id
        )

    response = []
    for result in relevant_documents:
        response.append(
            {
                "name": result.name,
                "distance": result.average_distance,
                "cross_encoding_score": result.cross_encoding_score,
            }
        )

    return response
