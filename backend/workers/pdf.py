import fitz
from PIL import Image
from shared.models.text_embedding import get_text_embedding_model
from shared.db_client import get_db_client
from workers.image import index_image

def load_pdf_from_path(path: str) -> fitz.Document:
    return fitz.open(path)

def process_pdf_document(db_document):
    document = load_pdf_from_path(db_document[3])
    index_pdf(db_document[0], document)

def index_pdf(document_id: int, document: fitz.Document):
    chunks: list[str] = []
    for page in document:
        pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
        index_image(document_id, image)
        for text_block in page.get_text_blocks():
            if '\x00' in text_block[4]:
                continue

            chunks.append(text_block[4].replace("\n", " "))   
    document.close()     

    text_embedding_model = get_text_embedding_model()
    text_embeddings = text_embedding_model.encode(chunks)
    with get_db_client() as connection:
        with connection.cursor() as cursor:
            for chunk, text_embedding in zip(chunks, text_embeddings):
                cursor.execute(
                    """
                    INSERT INTO document_embeddings (document_id, content, text_embedding)
                    VALUES (%s, %s, %s)
                    """,
                    (document_id, chunk, text_embedding)
                )

        connection.commit()