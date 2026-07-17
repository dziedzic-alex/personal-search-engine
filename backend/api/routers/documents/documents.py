import enum
import os
import zipfile
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import Field
from sqlalchemy import delete, select
from starlette.background import BackgroundTask

from api.dependencies import S3ClientDep, SessionDep, UserDep
from api.dependencies.sqs import SQSDocumentProcessingClientDep
from api.routers.documents.upload_utils import (
    is_allowed_content_type,
    persist_file,
    sanitize_content_type,
)
from api.schemas.camel_model import CamelModel
from db.models.document import Document, DocumentStatus
from db.repositories.documents import (
    DOCUMENT_LIST_PAGE_SIZE,
    DocumentRepository,
    FilterConfig,
    SortConfig,
)
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


class ListDocumentsRequest(CamelModel):
    query: str | None = None
    sort_config: SortConfig | None = None
    filter_config: FilterConfig | None = None
    page: int = Field(0, ge=0)


class ListDocumentsResponse(CamelModel):
    documents: list[ApiDocument]
    next_page: int | None = Field(None, ge=0)


@router.post("/list")
def get_documents(
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
    request: ListDocumentsRequest,
) -> ListDocumentsResponse:
    documents = DocumentRepository(session).get_documents(
        user.id,
        request.query,
        request.sort_config,
        request.filter_config,
        request.page,
    )

    next_page = None

    if len(documents) == DOCUMENT_LIST_PAGE_SIZE:
        next_page = request.page + 1

    return ListDocumentsResponse(
        documents=[to_api_document(document, s3_client) for document in documents],
        next_page=next_page,
    )


@router.get("/suggest")
def suggest_documents(
    query: str,
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
) -> list[ApiDocument]:
    documents = DocumentRepository(session).suggest_documents(user.id, query)

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


class DeleteDocumentsRequest(CamelModel):
    document_ids: list[int] = Field(min_length=1)


@router.delete("/bulk-delete", status_code=204)
def delete_documents(
    request: DeleteDocumentsRequest,
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
):
    documents_to_delete = session.scalars(
        select(Document)
        .where(Document.user_id == user.id)
        .where(Document.id.in_(request.document_ids))
    ).all()

    if len(documents_to_delete) != len(request.document_ids):
        raise HTTPException(status_code=404, detail="One or more documents not found")

    session.execute(
        delete(Document)
        .where(Document.user_id == user.id)
        .where(Document.id.in_([document.id for document in documents_to_delete]))
    )
    session.commit()

    content_keys = [document.s3_content_key for document in documents_to_delete]
    thumbnail_keys = [document.s3_thumbnail_key for document in documents_to_delete]

    try:
        s3_client.delete_files(content_keys + thumbnail_keys)
    except Exception as e:
        print(f"Error deleting documents {request.document_ids} from S3: {e}")
        pass


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

    try:
        s3_client.delete_files([document.s3_content_key, document.s3_thumbnail_key])
    except Exception as e:
        print(f"Error deleting document {document.id} from S3: {e}")
        pass


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

    existing_document = session.scalars(
        select(Document)
        .where(Document.user_id == user.id)
        .where(Document.name == request.name)
    ).first()
    if existing_document is not None:
        raise HTTPException(
            status_code=409, detail="Document with given name already exists"
        )

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
            s3_client, file_data, user.id, content_type
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


MAX_BULK_DOWNLOAD_GB = 2
MAX_BULK_DOWNLOAD_BYTE_SIZE = MAX_BULK_DOWNLOAD_GB * 1024 * 1024 * 1024


class DownloadDocumentsRequest(CamelModel):
    document_ids: list[int] = Field(min_length=2)


@router.post("/bulk-download")
def download_documents(
    request: DownloadDocumentsRequest,
    session: SessionDep,
    user: UserDep,
    s3_client: S3ClientDep,
):
    documents_to_download = session.scalars(
        select(Document)
        .where(Document.user_id == user.id)
        .where(Document.id.in_(request.document_ids))
    ).all()

    if len(documents_to_download) != len(request.document_ids):
        raise HTTPException(status_code=404, detail="One or more documents not found")

    total_byte_size = sum(document.size_bytes for document in documents_to_download)
    if total_byte_size > MAX_BULK_DOWNLOAD_BYTE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Total size of selected files exceeds {MAX_BULK_DOWNLOAD_GB}GB",
        )

    tmp = NamedTemporaryFile(delete=False)
    try:
        with zipfile.ZipFile(tmp, "w") as zip_file_stream:
            for document in documents_to_download:
                zip_file_stream.writestr(
                    document.name,
                    s3_client.get_file(document.s3_content_key),
                )

        tmp.close()

        return FileResponse(
            tmp.name,
            media_type="application/zip",
            background=BackgroundTask(os.unlink, tmp.name),
        )
    except Exception:
        tmp.close()
        os.unlink(tmp.name)
        raise
