import fitz
from datetime import timezone
from db.session import SessionLocal
from db.models.document import Document
from sqlalchemy import update
from pypdf._utils import parse_iso8824_date
from workers.text_quality import PDF_TEXT_BLOCK_PROFILE, passes_text_quality_checks

MIN_PAGE_TEXT_LENGTH = 200


def is_text_block_usable(text_block: str) -> bool:
    if not text_block or not text_block.strip():
        return False

    # Binary junk often includes null bytes and other C0 control characters.
    if any(ord(char) < 32 and char not in "\n\r\t" for char in text_block):
        return False

    # A few undecodable glyphs may appear in otherwise good text; strip and re-check.
    without_replacement_chars = text_block.replace("\ufffd", "")

    return passes_text_quality_checks(without_replacement_chars, PDF_TEXT_BLOCK_PROFILE)


def should_fallback_to_image(text: str) -> bool:
    return len(text) < MIN_PAGE_TEXT_LENGTH


def extract_pdf_metadata(document: fitz.Document, document_id: int):
    metadata = document.metadata
    if not metadata:
        return

    source_created_time = metadata.get("creationDate")

    if not source_created_time:
        source_created_time = metadata.get("modDate")

    if not source_created_time:
        return

    try:
        source_created_time = parse_iso8824_date(source_created_time)
    except ValueError:
        return

    if source_created_time.tzinfo is not None:
        source_created_time = source_created_time.astimezone(timezone.utc).replace(tzinfo=None)

    with SessionLocal() as session:
        session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(source_created_time=source_created_time)
        )
        session.commit()
