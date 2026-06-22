import json
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import select

from api.dependencies import S3ClientDep, SessionDep, UserDep
from api.routers.documents import ApiDocument, to_api_document
from api.routers.upload.upload_utils import (
    is_allowed_content_type,
    persist_file,
    sanitize_content_type,
)
from api.schemas.camel_model import CamelModel
from db.models import Document
from shared.content_type import ContentType
from shared.redis_client import get_redis_client

router = APIRouter(prefix="/upload", tags=["upload"])

UploadFiles = Annotated[list[UploadFile], File(...)]


class UploadFilesResponse(CamelModel):
    files_being_processed: list[ApiDocument]
    errors: list[str]


@router.post("/")
def upload_files(
    files: UploadFiles, user: UserDep, session: SessionDep, s3_client: S3ClientDep
) -> UploadFilesResponse:
    uploaded_files: UploadFilesResponse = UploadFilesResponse(
        files_being_processed=[], errors=[]
    )

    redis_client = get_redis_client()

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

        redis_client.lpush("jobs:upload", json.dumps({"document_id": document.id}))
        uploaded_files.files_being_processed.append(
            to_api_document(document, s3_client)
        )

    return uploaded_files
