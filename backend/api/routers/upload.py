from pathlib import Path
import shutil
import hashlib
import json
from shared.redis_client import get_redis_client
from shared.db_client import get_db_client

from fastapi import APIRouter
from fastapi import UploadFile, File

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/")
def upload_files(files: list[UploadFile] = File(...)):
    files_being_processed: list[dict] = []

    redis_client = get_redis_client()

    with get_db_client() as connection:
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

            document_id = None
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO documents (name, status, content_url, content_hash, content_type)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id 
                    """,
                    (filename, "pending", str(destination), content_hash, sanitized_content_type)
                )
                document_id = cursor.fetchone()[0]
            connection.commit()

            if document_id:
                redis_client.lpush("jobs:upload", json.dumps({"document_id": document_id}))
                files_being_processed.append({"filename": file.filename, "status": "pending"})

    return {"files_being_processed": files_being_processed}

        
    
