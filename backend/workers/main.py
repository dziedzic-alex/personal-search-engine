import json

from pillow_heif import register_heif_opener

from db.models.document import MAX_NUM_ATTEMPTS, Document, DocumentStatus
from db.session import SessionLocal
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES, ContentType
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.redis_client import get_redis_client
from shared.s3_client import get_s3_client
from workers.image.image import process_image_document
from workers.pdf.pdf import process_pdf_document
from sqlalchemy import delete
from db.models.document_embedding import DocumentEmbedding

register_heif_opener()


def main():
    print("Worker is running")

    get_text_embedding_model()
    get_image_embedding_model()
    get_s3_client()

    redis_client = get_redis_client()

    print("Models and clients initialized")

    while True:
        job = redis_client.brpop("jobs:upload", timeout=5)

        if not job:
            continue

        _, job_data = job
        job_data = json.loads(job_data)

        print(f"Processing job: {job_data}")

        with SessionLocal(expire_on_commit=False) as session:
            document: Document | None = session.get(Document, job_data["document_id"])

            if document is None:
                print(f"Document {job_data['document_id']} not found. Skipping...")
                continue

            if document.num_attempts >= MAX_NUM_ATTEMPTS:
                print(
                    f"Document {document.name} has reached the maximum number of processing attempts. Skipping..."
                )
                continue

            document.num_attempts += 1
            document.status = DocumentStatus.PROCESSING
            session.execute(
                delete(DocumentEmbedding).where(
                    DocumentEmbedding.document_id == document.id
                )
            )
            session.commit()

        try:
            if document.content_type in IMAGE_CONTENT_TYPE_VALUES:
                process_image_document(document)
            elif document.content_type == ContentType.PDF.value:
                process_pdf_document(document)
            else:
                raise ValueError(f"Unsupported document type: {document.content_type}")

            with SessionLocal(expire_on_commit=False) as session:
                document = session.get(Document, job_data["document_id"])
                document.status = DocumentStatus.PROCESSED
                session.commit()

            print(f"Document {document.name} successfully processed")

        except Exception as e:
            print(f"Error processing document {document.name}: {e}")

            with SessionLocal() as session:
                document = session.get(Document, job_data["document_id"])
                document.status = DocumentStatus.FAILED
                session.commit()


if __name__ == "__main__":
    main()
