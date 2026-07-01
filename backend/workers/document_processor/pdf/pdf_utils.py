from datetime import UTC

import fitz
from pypdf._utils import parse_iso8824_date
from sqlalchemy import update

from db.models.document import Document
from db.session import SessionLocal
from workers.document_processor.text_quality import PDF_TEXT_BLOCK_PROFILE, passes_text_quality_checks

MIN_PAGE_TEXT_LENGTH = 200
MIN_CHUNK_CHARS = 300
MAX_CHUNK_CHARS = 1500
MIN_INDEXABLE_CHARS = 50


def merge_text_blocks_into_chunks(blocks: list[str]) -> list[str]:
    chunks: list[str] = []
    buffer = ""

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        buffer = f"{buffer} {block}".strip() if buffer else block

        while len(buffer) >= MIN_CHUNK_CHARS:
            if len(buffer) <= MAX_CHUNK_CHARS:
                chunks.append(buffer)
                buffer = ""
                break

            split_point = buffer.rfind(" ", MIN_CHUNK_CHARS, MAX_CHUNK_CHARS + 1)
            if split_point == -1:
                split_point = MAX_CHUNK_CHARS
            chunks.append(buffer[:split_point].strip())
            buffer = buffer[split_point:].strip()

    if not buffer:
        return chunks

    if len(buffer) >= MIN_INDEXABLE_CHARS or not chunks:
        chunks.append(buffer)
    else:
        chunks[-1] = f"{chunks[-1]} {buffer}".strip()

    return chunks


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
        source_created_time = source_created_time.astimezone(UTC).replace(tzinfo=None)

    with SessionLocal() as session:
        session.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(source_created_time=source_created_time)
        )
        session.commit()
