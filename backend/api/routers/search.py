from fastapi import APIRouter
from db.repositories.documents import DocumentRepository
from db.session import get_session
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search(query: str, session: Session = Depends(get_session)):
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
