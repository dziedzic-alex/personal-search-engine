import hashlib
import json
import shutil
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from api.routers.upload.upload_utils import (
    is_allowed_content_type,
    sanitize_content_type,
)
from db.models import Document
from db.session import SessionLocal
from shared.redis_client import get_redis_client

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[3] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

UploadFiles = Annotated[list[UploadFile], File(...)]


@router.post("/")
def upload_files(files: UploadFiles):
    files_being_processed: list[dict] = []

    redis_client = get_redis_client()

    with SessionLocal() as session:
        for file in files:
            filename = file.filename

            sanitized_content_type = sanitize_content_type(file.content_type, filename)

            if not is_allowed_content_type(sanitized_content_type):
                continue

            destination = UPLOAD_DIR / filename
            with open(destination, "wb") as f:
                shutil.copyfileobj(file.file, f)

            content_hash = hashlib.sha256(destination.read_bytes()).hexdigest()

            document = Document(
                name=filename,
                content_url=str(destination),
                content_hash=content_hash,
                content_type=sanitized_content_type,
            )

            session.add(document)
            session.commit()

            redis_client.lpush("jobs:upload", json.dumps({"document_id": document.id}))
            files_being_processed.append(
                {"filename": file.filename, "status": "pending"}
            )

    return {"files_being_processed": files_being_processed}
