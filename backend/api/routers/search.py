from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.repositories.documents import DocumentRepository
from db.session import get_session

router = APIRouter(prefix="/search", tags=["search"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/")
def search(query: str, session: SessionDep):
    relevant_documents = DocumentRepository(session).get_relevant_documents(query)

    response = []
    for document in relevant_documents:
        response.append(
            {
                "name": document.name,
                "distance": document.distance,
            }
        )

    return response
