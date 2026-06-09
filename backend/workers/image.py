import pytesseract
from PIL import Image, ImageOps

from db.models.document import Document
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model

MIN_IMAGE_WIDTH = 64
MIN_IMAGE_HEIGHT = 64


def load_image_from_path(path: str) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")

    return image


def process_image_document(document: Document):
    image = load_image_from_path(document.content_url)
    index_image(document.id, image)


def should_index(image: Image.Image) -> bool:
    return image.width >= MIN_IMAGE_WIDTH and image.height >= MIN_IMAGE_HEIGHT

def index_image(document_id: int, image: Image.Image) -> bool:
    if not should_index(image):
        return False

    image_embedding = get_image_embedding_model().encode(image)

    gray = image.convert("L")
    text = pytesseract.image_to_string(gray).strip()
    text_embedding = None
    if text:
        text_embedding = get_text_embedding_model().encode(text)

    with SessionLocal() as session:
        session.add(
            DocumentEmbedding(document_id=document_id, image_embedding=image_embedding)
        )

        if text_embedding is not None:
            session.add(
                DocumentEmbedding(
                    document_id=document_id, content=text, text_embedding=text_embedding
                )
            )

        session.commit()

    return True
