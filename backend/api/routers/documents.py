from datetime import datetime

from fastapi import APIRouter
from sqlalchemy import select

from api.dependencies import SessionDep, UserDep
from api.schemas.camel_model import CamelModel
from db.models.document import Document, DocumentStatus, MAX_NUM_ATTEMPTS
from shared.content_category import ContentCategory, content_type_to_category
from fastapi import HTTPException
import json
from shared.redis_client import get_redis_client

router = APIRouter(prefix="/documents", tags=["documents"])


class ApiDocument(CamelModel):
    id: int
    name: str
    content_category: ContentCategory
    status: DocumentStatus
    num_attempts: int
    content_url: str
    thumbnail_url: str
    size: int
    source_created_time: datetime | None
    uploaded_time: datetime

class DocumentsResponse(CamelModel):
    documents: list[ApiDocument]

@router.get("/")
def get_documents(session: SessionDep, user: UserDep) -> DocumentsResponse:
    documents = session.scalars(select(Document).where(Document.user_id == user.id)).all()
    
    response_documents = []
    for document in documents:
        response_documents.append(ApiDocument(
            id=document.id,
            name=document.name,
            content_category=content_type_to_category(document.content_type),
            status=DocumentStatus(document.status),
            num_attempts=document.num_attempts,
            content_url=document.content_url,
            thumbnail_url=document.thumbnail_url,
            size=document.size_bytes,
            source_created_time=document.source_created_time,
            uploaded_time=document.created_time,
        ))

    return DocumentsResponse(documents=response_documents)

@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, session: SessionDep, user: UserDep) -> None:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session.delete(document)
    session.commit()


class DocumentUpdateRequest(CamelModel):
    name: str

@router.patch("/{document_id}")
def update_document(document_id: int, request: DocumentUpdateRequest, session: SessionDep, user: UserDep) -> ApiDocument:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    document.name = request.name
    session.commit()

    return ApiDocument(
        id=document.id,
        name=document.name,
        content_category=content_type_to_category(document.content_type),
        status=DocumentStatus(document.status),
        num_attempts=document.num_attempts,
        content_url=document.content_url,
        thumbnail_url=document.thumbnail_url,
        size=document.size_bytes,
        source_created_time=document.source_created_time,
        uploaded_time=document.created_time,
    )

@router.post("/{document_id}/retry")
def retry_document(document_id: int, session: SessionDep, user: UserDep) -> ApiDocument:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    if document.num_attempts >= MAX_NUM_ATTEMPTS:
        raise HTTPException(status_code=400, detail="Document has reached the maximum number of processing attempts")

    document.status = DocumentStatus.PENDING
    session.commit()
    get_redis_client().lpush("jobs:upload", json.dumps({"document_id": document.id}))

    return ApiDocument(
        id=document.id,
        name=document.name,
        content_category=content_type_to_category(document.content_type),
        status=DocumentStatus(document.status),
        num_attempts=document.num_attempts,
        content_url=document.content_url,
        thumbnail_url=document.thumbnail_url,
        size=document.size_bytes,
        source_created_time=document.source_created_time,
        uploaded_time=document.created_time,
    )