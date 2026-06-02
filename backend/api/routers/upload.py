import hashlib
import json
import shutil
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from db.models.document import Document
from db.session import SessionLocal
from shared.redis_client import get_redis_client

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/")
def upload_files(files: list[UploadFile] = File(...)):
    files_being_processed: list[dict] = []

    redis_client = get_redis_client()

    with SessionLocal() as session:
        for file in files:
            filename = file.filename

            destination = UPLOAD_DIR / filename
            with open(destination, "wb") as f:
                shutil.copyfileobj(file.file, f)

            content_hash = hashlib.sha256(destination.read_bytes()).hexdigest()

            sanitized_content_type = file.content_type.split("/")[1]
            if sanitized_content_type == "octet-stream":
                extension = filename.split(".").pop().lower()
                sanitized_content_type = extension

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
