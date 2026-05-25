from fastapi import APIRouter
from fastapi import UploadFile, File

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/")
def upload_files(files: list[UploadFile] = File(...)):
    return {"files": [file.filename for file in files]}
