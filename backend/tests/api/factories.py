from datetime import datetime

from db.models.document import Document, DocumentStatus


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
