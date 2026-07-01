import enum
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from sqlalchemy import select

from api.dependencies import S3ClientDep, SessionDep, UserDep
from api.routers.documents.upload_utils import (
    is_allowed_content_type,
    persist_file,
    sanitize_content_type,
)
from api.schemas.camel_model import CamelModel
from api.dependencies.sqs import SQSDocumentProcessingClientDep
from db.models.document import Document, DocumentStatus
from db.repositories.documents import DocumentRepository
from shared.content_category import ContentCategory, content_type_to_category
from shared.content_type import ContentType
from shared.s3_client import S3Client

router = APIRouter(prefix="/documents", tags=["documents"])


class ApiDocument(CamelModel):
    id: int
    name: str
    content_category: ContentCategory
    status: DocumentStatus
    preview_url: str
    download_url: str
    thumbnail_url: str
    size: int
    source_created_time: datetime | None
    uploaded_time: datetime


def to_api_document(document: Document, s3_client: S3Client) -> ApiDocument:
    return ApiDocument(
        id=document.id,
        name=document.name,
        content_category=content_type_to_category(document.content_type),
        status=DocumentStatus(document.status),
        preview_url=s3_client.generate_presigned_url(document.s3_content_key),
        download_url=s3_client.generate_presigned_url(
            document.s3_content_key,
            content_disposition_config=S3Client.ContentDispositionConfig(
                filename=document.name
            ),
        ),
        thumbnail_url=s3_client.generate_presigned_url(document.s3_thumbnail_key),
        size=document.size_bytes,
        source_created_time=document.source_created_time,
        uploaded_time=document.created_time,
    )


@router.get("/list")
def get_documents(
    session: SessionDep, user: UserDep, s3_client: S3ClientDep, query: str | None = None
) -> list[ApiDocument]:
    documents = DocumentRepository(session).get_documents(user.id, query)

    return [to_api_document(document, s3_client) for document in documents]


class SearchMode(enum.StrEnum):
    TEXT = "text"
    IMAGE = "image"


@router.get("/search")
def search(
    query: str,
    search_mode: SearchMode,
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
) -> list[ApiDocument]:
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
        response.append(to_api_document(result, s3_client))

    return response


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int, session: SessionDep, user: UserDep, s3_client: S3ClientDep
) -> None:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    session.delete(document)
    session.commit()

    s3_client.delete_file(document.s3_content_key)
    s3_client.delete_file(document.s3_thumbnail_key)


class DocumentUpdateRequest(CamelModel):
    name: str


@router.patch("/{document_id}")
def update_document(
    document_id: int,
    request: DocumentUpdateRequest,
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
) -> ApiDocument:
    document = session.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    document.name = request.name
    session.commit()

    return to_api_document(document, s3_client)


UploadFiles = Annotated[list[UploadFile], File(...)]


class UploadFilesResponse(CamelModel):
    files_being_processed: list[ApiDocument]
    errors: list[str]


@router.post("/")
def upload_files(
    files: UploadFiles,
    user: UserDep,
    session: SessionDep,
    s3_client: S3ClientDep,
    sqs_client: SQSDocumentProcessingClientDep,
) -> UploadFilesResponse:
    uploaded_files: UploadFilesResponse = UploadFilesResponse(
        files_being_processed=[], errors=[]
    )

    for file in files:
        filename = file.filename

        if not filename:
            uploaded_files.errors.append("Missing filename")
            continue

        sanitized_content_type = sanitize_content_type(file.content_type, filename)

        if not is_allowed_content_type(sanitized_content_type):
            if (
                f"Content type {file.content_type} not allowed"
                not in uploaded_files.errors
            ):
                uploaded_files.errors.append(
                    f"Content type {file.content_type} not allowed"
                )
            continue

        existing_document = session.scalars(
            select(Document)
            .where(Document.user_id == user.id)
            .where(Document.name == filename)
        ).first()

        if existing_document is not None:
            print(f"Document {filename} already exists. Skipping...")
            uploaded_files.errors.append(f"Document {filename} already exists")
            continue

        file_data = file.file.read()
        content_type = ContentType(sanitized_content_type)
        persisted_file_object_keys = persist_file(
            s3_client, filename, file_data, user.id, content_type
        )

        try:
            document = Document(
                user_id=user.id,
                name=filename,
                s3_content_key=persisted_file_object_keys.content_key,
                s3_thumbnail_key=persisted_file_object_keys.thumbnail_key,
                content_type=content_type.value,
                size_bytes=len(file_data),
            )

            session.add(document)
            session.commit()
        except Exception as e:
            print(f"Error saving document {filename}: {e}")
            session.rollback()
            s3_client.delete_file(persisted_file_object_keys.content_key)
            s3_client.delete_file(persisted_file_object_keys.thumbnail_key)
            uploaded_files.errors.append(f"Error saving document {filename}")
            continue

        try:
            sqs_client.submit_document_message(document.id, user.id)
        except Exception as e:
            print(f"Error submitting document {filename} for processing: {e}")
            session.delete(document)
            session.commit()
            s3_client.delete_file(persisted_file_object_keys.content_key)
            s3_client.delete_file(persisted_file_object_keys.thumbnail_key)
            uploaded_files.errors.append(
                f"Error submitting document {filename} for processing"
            )
            continue

        uploaded_files.files_being_processed.append(
            to_api_document(document, s3_client)
        )

    return uploaded_files
