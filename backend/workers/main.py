from shared.redis_client import get_redis_client
from pathlib import Path
import json
import fitz
from sentence_transformers import SentenceTransformer
from shared.db_client import get_db_client

def main():
    print('Worker is running')

    model = SentenceTransformer("all-MiniLM-L6-v2")

    redis_client = get_redis_client()

    while True:
        job = redis_client.brpop("jobs:upload", timeout=5)

        if not job:
            continue

        queue_name, job_data = job
        job_data = json.loads(job_data)

        print(f"Processing job: {job_data}")

        with get_db_client() as connection:
            db_document = None
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM documents WHERE id = %s", 
                    (job_data['document_id'],)
                )
                db_document = cursor.fetchone()

            document: fitz.Document = fitz.open(db_document[3])
            chunks: list[str] = []
            for page in document:
                for text_block in page.get_text_blocks():
                    chunks.append(text_block[4].replace("\n", " "))

            embeddings = model.encode(chunks)
            with connection.cursor() as cursor:
                for chunk, embedding in zip(chunks, embeddings):
                    cursor.execute(
                        """
                        INSERT INTO chunks (document_id, content, embedding)
                        VALUES (%s, %s, %s)
                        """,
                        (db_document[0], chunk, embedding)
                    )

                connection.commit()
        
        print(f"Document {db_document[1]} processed")



if __name__ == "__main__":
    main()