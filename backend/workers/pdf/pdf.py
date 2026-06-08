import fitz
from PIL import Image

from db.models.document import Document
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.models.text_embedding import get_text_embedding_model
from workers.image import index_image
from workers.pdf.pdf_utils import is_text_block_usable, sanitize_text_block


def load_pdf_from_path(path: str) -> fitz.Document:
    return fitz.open(path)


def process_pdf_document(db_document: Document):
    pdf = load_pdf_from_path(db_document.content_url)
    index_pdf(db_document.id, pdf)


def index_pdf(document_id: int, document: fitz.Document):
    chunks: list[str] = []
    for page in document:
        pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
        index_image(document_id, image)
        for text_block in page.get_text_blocks():
            if not is_text_block_usable(text_block[4]):
                continue

            chunks.append(sanitize_text_block(text_block[4]))
    document.close()

    text_embedding_model = get_text_embedding_model()
    text_embeddings = text_embedding_model.encode(chunks)
    with SessionLocal() as session:
        for chunk, text_embedding in zip(chunks, text_embeddings, strict=True):
            session.add(
                DocumentEmbedding(
                    document_id=document_id,
                    content=chunk,
                    text_embedding=text_embedding,
                )
            )

        session.commit()
