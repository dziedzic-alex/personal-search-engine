from PIL import Image, ImageOps
from shared.db_client import get_db_client
import pytesseract
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model

def load_image_from_path(path: str) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")

    return image

def process_image_document(db_document):
    image = load_image_from_path(db_document[3])
    index_image(db_document[0], image)

def index_image(document_id: int, image: Image.Image):
    image_embedding = get_image_embedding_model().encode(image)

    gray = image.convert("L")
    text = pytesseract.image_to_string(gray).strip()
    text_embedding = None
    if text:
        text_embedding = get_text_embedding_model().encode(text)

    with get_db_client() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO document_embeddings (document_id, image_embedding) VALUES (%s, %s)",
                (document_id, image_embedding),
            )
            if text_embedding is not None:
                cursor.execute(
                    "INSERT INTO document_embeddings (document_id, content, text_embedding) VALUES (%s, %s, %s)",
                    (document_id, text, text_embedding),
                )
        connection.commit()