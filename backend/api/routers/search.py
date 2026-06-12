import enum
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.search_mode import SearchMode

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
        relevant_documents = DocumentRepository(session).get_relevant_text_documents(query)
    elif search_mode == SearchMode.IMAGE:
        relevant_documents = DocumentRepository(session).get_relevant_image_documents(query)

    response = []
    for rrf_score, document, cross_encoding_score in relevant_documents:
        response.append(
            {
                "name": document.name,
                "distance": document.average_distance,
                "rrf_score": rrf_score,
                "cross_encoding_score": cross_encoding_score
            }
        )

    return response
