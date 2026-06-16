import json
import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select

from api.routers.upload.upload_utils import (
    is_allowed_content_type,
    sanitize_content_type,
)
from db.models import Document
from db.models.user import User
from db.session import SessionLocal
from shared.content_type import ContentType
from shared.redis_client import get_redis_client
from api.routers.auth.auth_utils import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

UploadFiles = Annotated[list[UploadFile], File(...)]

UserDep = Annotated[User, Depends(get_current_user)]

@router.post("/")
def upload_files(files: UploadFiles, user: UserDep):
    files_being_processed: list[dict] = []

    redis_client = get_redis_client()

    with SessionLocal() as session:
        for file in files:
            filename = file.filename

            sanitized_content_type = sanitize_content_type(file.content_type, filename)

            if not is_allowed_content_type(sanitized_content_type):
                files_being_processed.append(
                    {
                        "filename": filename,
                        "status": "skipped",
                        "error": "Content type not allowed",
                    }
                )
                continue

            existing_document = session.scalars(
                select(Document).where(Document.user_id == user.id).where(Document.name == filename)
            ).first()

            if existing_document is not None:
                print(f"Document {filename} already exists. Skipping...")
                files_being_processed.append(
                    {
                        "filename": filename,
                        "status": "skipped",
                        "error": "already exists",
                    }
                )
                continue

            destination = UPLOAD_DIR / filename
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
            files_being_processed.append(
                {"filename": file.filename, "status": "pending"}
            )

    return {"files_being_processed": files_being_processed}
