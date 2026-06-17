import enum

from fastapi import APIRouter

from api.dependencies import SessionDep, UserDep
from db.repositories.documents import DocumentRepository

router = APIRouter(prefix="/search", tags=["search"])


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
