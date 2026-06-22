import enum
from io import BytesIO

import pytesseract
from PIL import Image

from db.models.document import Document
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from workers.image.image_utils import extract_image_metadata
from workers.text_quality import (
    OCR_PDF_EMBEDDED_PROFILE,
    OCR_PDF_PAGE_PROFILE,
    OCR_PHOTO_PROFILE,
    TextQualityProfile,
    passes_text_quality_checks,
    sanitize_text,
)
from shared.s3_client import get_s3_client
from shared.image_utils import normalize_image

MIN_IMAGE_WIDTH = 64
MIN_IMAGE_HEIGHT = 64
# Long OCR on a direct upload usually means a photo of a document, not a caption.
PHOTO_DOCUMENT_OCR_LENGTH = 200


class ImageIndexContext(enum.StrEnum):
    PHOTO = "photo"
    PDF_PAGE = "pdf_page"
    PDF_EMBEDDED = "pdf_embedded"


OCR_PROFILES: dict[ImageIndexContext, TextQualityProfile] = {
    ImageIndexContext.PHOTO: OCR_PHOTO_PROFILE,
    ImageIndexContext.PDF_PAGE: OCR_PDF_PAGE_PROFILE,
    ImageIndexContext.PDF_EMBEDDED: OCR_PDF_EMBEDDED_PROFILE,
}


def _load_image_from_s3(s3_content_key: str) -> Image.Image:
    s3_client = get_s3_client()
    image = Image.open(BytesIO(s3_client.get_file(s3_content_key)))
    image = normalize_image(image)

    return image


def process_image_document(document: Document):
    image = _load_image_from_s3(document.s3_content_key)
    extract_image_metadata(image, document.id)
    index_image(document.id, image, context=ImageIndexContext.PHOTO)


def _should_index(image: Image.Image) -> bool:
    return image.width >= MIN_IMAGE_WIDTH and image.height >= MIN_IMAGE_HEIGHT


def should_encode_image_embedding(
    context: ImageIndexContext,
    text: str,
    *,
    has_text_embedding: bool,
) -> bool:
    if context == ImageIndexContext.PHOTO:
        return not has_text_embedding or len(text) < PHOTO_DOCUMENT_OCR_LENGTH
    return not has_text_embedding


def index_image(
    document_id: int,
    image: Image.Image,
    *,
    context: ImageIndexContext = ImageIndexContext.PHOTO,
) -> bool:
    if not _should_index(image):
        return False

    gray = image.convert("L")
    text = sanitize_text(pytesseract.image_to_string(gray).strip())

    text_embedding = None
    if text and passes_text_quality_checks(text, OCR_PROFILES[context]):
        text_embedding = get_text_embedding_model().encode(text)

    image_embedding = None
    if should_encode_image_embedding(
        context, text, has_text_embedding=text_embedding is not None
    ):
        image_embedding = get_image_embedding_model().encode(image)

    with SessionLocal() as session:
        if image_embedding is not None:
            session.add(
                DocumentEmbedding(
                    document_id=document_id, image_embedding=image_embedding
                )
            )

        if text_embedding is not None:
            session.add(
                DocumentEmbedding(
                    document_id=document_id, content=text, text_embedding=text_embedding
                )
            )

        session.commit()

    return True
