from io import BytesIO

import fitz
from PIL import Image

from db.models.document import Document
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.models.text_embedding import get_text_embedding_model
from workers.image import ImageIndexContext, index_image
from workers.pdf.pdf_utils import is_text_block_usable, should_fallback_to_image
from workers.text_quality import sanitize_text


def load_pdf_from_path(path: str) -> fitz.Document:
    return fitz.open(path)


def process_pdf_document(db_document: Document):
    pdf = load_pdf_from_path(db_document.content_url)
    index_pdf(db_document.id, pdf)

def index_pdf(document_id: int, document: fitz.Document):
    chunks: list[str] = []
    processed_image_xrefs: set[int] = set()
    for page in document:
        page_chunks: list[str] = []
        for text_block in page.get_text_blocks():
            if not is_text_block_usable(text_block[4]):
                continue

            page_chunks.append(sanitize_text(text_block[4]))

        page_text = " ".join(page_chunks)
        images = page.get_images()

        page_image_indexed = False
        for image in images:
            xref = image[0]

            if xref in processed_image_xrefs:
                continue
            processed_image_xrefs.add(xref)

            try:
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(BytesIO(image_bytes)).convert("RGB")
                if index_image(
                    document_id, image, context=ImageIndexContext.PDF_EMBEDDED
                ):
                    page_image_indexed = True
            except Exception as e:
                print(f"Error extracting image {xref} from page {page.number} in document {document_id}: {e}")
                continue

        should_fallback = should_fallback_to_image(page_text)
        if should_fallback and not page_image_indexed:
            pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
            index_image(document_id, image, context=ImageIndexContext.PDF_PAGE)

        if not should_fallback:
            chunks.extend(page_chunks)

    document.close()

    if not chunks:
        print(f"No text chunks found for document {document_id}")
        return

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
