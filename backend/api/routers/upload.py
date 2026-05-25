from pathlib import Path
import shutil
import uuid

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
    saved_files: list[str] = []
    for file in files:

        filename = get_safe_filename(file.filename)

        destination = UPLOAD_DIR / filename
        with open(destination, "wb") as f:
            shutil.copyfileobj(file.file, f)

        saved_files.append(filename)

    return {"files": saved_files}

        
    
