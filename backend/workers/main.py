from shared.redis_client import get_redis_client
import json
from shared.db_client import get_db_client
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

        db_document = None
        with get_db_client() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM documents WHERE id = %s", 
                    (job_data['document_id'],)
                )
                db_document = cursor.fetchone()

        if db_document[6] == "jpeg" or db_document[6] == "jpg" or db_document[6] == "png" or \
        db_document[6] == "webp" or db_document[6] == "heic" or db_document[6] == "heif":
            process_image_document(db_document)
        elif db_document[6] == "pdf":
            process_pdf_document(db_document)
        else:
            print(f"Unsupported document type: {db_document[6]}. Skipping...")
            continue
                
        print(f"Document {db_document[1]} processed")



if __name__ == "__main__":
    main()