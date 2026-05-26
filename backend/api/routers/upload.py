from pathlib import Path
import shutil
import uuid
import json
from shared.redis_client import get_redis_client

from fastapi import APIRouter
from fastapi import UploadFile, File

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path(__file__).parents[2] / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

def get_safe_filename(name: str | None) -> str:
    if not name:
        return f"{uuid.uuid4()}_unnamed.pdf"

    return f"{uuid.uuid4()}_{Path(name).name}"

@router.post("/")
def upload_files(files: list[UploadFile] = File(...)):
    files_being_processed: list[dict] = []

    redis_client = get_redis_client()

    for file in files:

        filename = get_safe_filename(file.filename)

        destination = UPLOAD_DIR / filename
        with open(destination, "wb") as f:
            shutil.copyfileobj(file.file, f)

        redis_client.lpush("jobs:upload", json.dumps({"filename": filename, "type": file.content_type, "path": str(destination)}))
        files_being_processed.append({"filename": file.filename, "status": "pending"})

    return {"files_being_processed": files_being_processed}

        
    
