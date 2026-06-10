import json

from pillow_heif import register_heif_opener

from db.models.document import Document, DocumentStatus
from db.session import SessionLocal
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES, ContentType
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.redis_client import get_redis_client
from workers.image import process_image_document
from workers.pdf.pdf import process_pdf_document

register_heif_opener()


def main():
    print("Worker is running")

    get_text_embedding_model()
    get_image_embedding_model()

    redis_client = get_redis_client()

    print("Models and clients initialized")

    while True:
        job = redis_client.brpop("jobs:upload", timeout=5)

        if not job:
            continue

        _, job_data = job
        job_data = json.loads(job_data)

        print(f"Processing job: {job_data}")

        content_type = None
        with SessionLocal() as session:
            document: Document = session.get(Document, job_data["document_id"])

            if document is None:
                print(f"Document {job_data['document_id']} not found. Skipping...")
                continue

            content_type = document.content_type

            document.status = DocumentStatus.PROCESSING
            session.commit()

        try:
            if content_type in IMAGE_CONTENT_TYPE_VALUES:
                process_image_document(document)
            elif content_type == ContentType.PDF.value:
                process_pdf_document(document)
            else:
                raise ValueError(f"Unsupported document type: {content_type}")

            with SessionLocal() as session:
                document = session.get(Document, job_data["document_id"])
                document.status = DocumentStatus.COMPLETED
                document.error = None
                session.commit()
                print(f"Document {document.name} successfully processed")


        except Exception as e:
            with SessionLocal() as session:
                document = session.get(Document, job_data["document_id"])
                document.status = DocumentStatus.FAILED
                document.error = str(e)
                session.commit()
                print(f"Error processing document {document.name}: {e}")
       


if __name__ == "__main__":
    main()
