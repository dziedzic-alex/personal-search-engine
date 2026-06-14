import enum
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.repositories.documents import DocumentRepository
from db.session import get_session

router = APIRouter(prefix="/search", tags=["search"])

SessionDep = Annotated[Session, Depends(get_session)]


class SearchMode(enum.StrEnum):
    TEXT = "text"
    IMAGE = "image"


@router.get("/")
def search(query: str, search_mode: SearchMode, session: SessionDep):
    if search_mode == SearchMode.TEXT:
        relevant_documents = DocumentRepository(session).get_relevant_text_documents(
            query
        )
    elif search_mode == SearchMode.IMAGE:
        relevant_documents = DocumentRepository(session).get_relevant_image_documents(
            query
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
