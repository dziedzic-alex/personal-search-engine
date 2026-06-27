import enum

from fastapi import APIRouter

from api.dependencies import SessionDep, UserDep, S3ClientDep
from api.routers.documents import ApiDocument, to_api_document
from db.repositories.documents import DocumentRepository

router = APIRouter(prefix="/search", tags=["search"])


class SearchMode(enum.StrEnum):
    TEXT = "text"
    IMAGE = "image"


@router.get("/")
def search(query: str, search_mode: SearchMode, session: SessionDep, user: UserDep, s3_client: S3ClientDep) -> list[ApiDocument]:
    if search_mode == SearchMode.TEXT:
        relevant_documents = DocumentRepository(session).get_relevant_text_documents(
            query, user.id
        )
    elif search_mode == SearchMode.IMAGE:
        relevant_documents = DocumentRepository(session).get_relevant_image_documents(
            query, user.id
        )

    response: list[ApiDocument] = []
    for result in relevant_documents:
        response.append(
            to_api_document(result, s3_client)
        )

    return response
