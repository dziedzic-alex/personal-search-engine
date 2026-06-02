from shared.redis_client import get_redis_client
import json
from db.session import SessionLocal
from db.models.document import Document
from pillow_heif import register_heif_opener
from workers.image import process_image_document
from workers.pdf import process_pdf_document
from shared.models.text_embedding import get_text_embedding_model
from shared.models.image_embedding import get_image_embedding_model

register_heif_opener()

def main():
    print('Worker is running')

    get_text_embedding_model()
    get_image_embedding_model()

    redis_client = get_redis_client()

    print("Models and clients initialized")

    while True:
        job = redis_client.brpop("jobs:upload", timeout=5)

        if not job:
            continue

        queue_name, job_data = job
        job_data = json.loads(job_data)

        print(f"Processing job: {job_data}")

        document = None
        with SessionLocal() as session:
            document = session.get(Document, job_data['document_id'])

        if document is None:
            print(f"Document {job_data['document_id']} not found. Skipping...")
            continue

        content_type = document.content_type

        if content_type == "jpeg" or content_type == "jpg" or content_type == "png" or \
        content_type == "webp" or content_type == "heic" or content_type == "heif":
            process_image_document(document)
        elif content_type == "pdf":
            process_pdf_document(document)
        else:
            print(f"Unsupported document type: {content_type}. Skipping...")
            continue
                
        print(f"Document {document.name} processed")



if __name__ == "__main__":
    main()