import json
import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from sqlalchemy import select

from api.dependencies import SessionDep, UserDep
from api.routers.upload.upload_utils import (
    is_allowed_content_type,
    sanitize_content_type,
)
from db.models import Document
from shared.content_type import ContentType
from shared.redis_client import get_redis_client
from api.routers.documents import ApiDocument
from api.schemas.camel_model import CamelModel
from db.models.document import DocumentStatus
from shared.content_category import content_type_to_category

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

UploadFiles = Annotated[list[UploadFile], File(...)]


class UploadFilesResponse(CamelModel):
    files_being_processed: list[ApiDocument]
    errors: list[str]


@router.post("/")
def upload_files(
    files: UploadFiles, user: UserDep, session: SessionDep
) -> UploadFilesResponse:
    uploaded_files: UploadFilesResponse = UploadFilesResponse(
        files_being_processed=[], errors=[]
    )

    redis_client = get_redis_client()

    for file in files:
        filename = file.filename

        sanitized_content_type = sanitize_content_type(file.content_type, filename)

        if (
            not is_allowed_content_type(sanitized_content_type)
            and "Content type not allowed" not in uploaded_files.errors
        ):
            uploaded_files.errors.append("Content type not allowed")
            continue

        existing_document = session.scalars(
            select(Document)
            .where(Document.user_id == user.id)
            .where(Document.name == filename)
        ).first()

        if (
            existing_document is not None
            and "Document already exists" not in uploaded_files.errors
        ):
            print(f"Document {filename} already exists. Skipping...")
            uploaded_files.errors.append("Document already exists")
            continue

        destination_dir = UPLOAD_DIR / str(user.id)
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / filename
        with open(destination, "wb") as f:
            shutil.copyfileobj(file.file, f)

        document = Document(
            user_id=user.id,
            name=filename,
            content_url=str(destination),
            content_type=ContentType(sanitized_content_type).value,
            size_bytes=destination.stat().st_size,
        )

        session.add(document)
        session.commit()

        redis_client.lpush("jobs:upload", json.dumps({"document_id": document.id}))
        uploaded_files.files_being_processed.append(
            ApiDocument(
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
        )

    return uploaded_files
