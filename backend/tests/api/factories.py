from datetime import datetime

from db.models.document import Document, DocumentStatus
from shared.content_category import content_type_to_category

PRESIGNED_URL_PREFIX = "https://presigned.example"


def make_document(**kwargs) -> Document:
    defaults = {
        "id": 1,
        "user_id": 1,
        "name": "report.pdf",
        "status": DocumentStatus.PROCESSED,
        "s3_content_key": "1/report.pdf",
        "s3_thumbnail_key": "1/thumbnail_report.jpg",
        "content_type": "pdf",
        "size_bytes": 1024,
        "source_created_time": None,
        "created_time": datetime(2025, 6, 1),
    }
    defaults.update(kwargs)
    return Document(**defaults)


def api_document_json(document: Document) -> dict:
    return {
        "id": document.id,
        "name": document.name,
        "contentCategory": content_type_to_category(document.content_type).value,
        "status": DocumentStatus(document.status).value,
        "previewUrl": f"{PRESIGNED_URL_PREFIX}/{document.s3_content_key}",
        "downloadUrl": f"{PRESIGNED_URL_PREFIX}/{document.s3_content_key}",
        "thumbnailUrl": f"{PRESIGNED_URL_PREFIX}/{document.s3_thumbnail_key}",
        "size": document.size_bytes,
        "sourceCreatedTime": document.source_created_time,
        "uploadedTime": document.created_time.isoformat(),
    }
