from shared.redis_client import get_redis_client
from pathlib import Path
import json
import fitz
from sentence_transformers import SentenceTransformer
from shared.db_client import get_db_client
from PIL import Image, ImageOps
import pytesseract
from transformers import pipeline
from pillow_heif import register_heif_opener

register_heif_opener()

def main():
    print('Worker is running')

    model = SentenceTransformer("all-MiniLM-L6-v2")
    caption_generator = pipeline("image-text-to-text", model="llava-hf/llava-v1.6-mistral-7b-hf")

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

            chunks: list[str] = []
            if db_document[6] == "jpeg" or db_document[6] == "jpg" or db_document[6] == "png" or \
            db_document[6] == "webp" or db_document[6] == "heic" or db_document[6] == "heif":
                print(f"Document {db_document[1]} is an image. Falling back to OCR and caption generation.")
                image = Image.open(db_document[3])
                image = ImageOps.exif_transpose(image)
                if image.mode not in ["RGB", "L"]:
                    image = image.convert("RGB")
                caption = caption_generator(image=image, text="Describe the image in detail.")
                print(caption)
                chunks.append(caption)
                image = image.convert("L")
                text = pytesseract.image_to_string(image)
                chunks.append(text)
                print(f"Image Processing Complete for document {db_document[1]}")
            else:
                document: fitz.Document = fitz.open(db_document[3])
                for page in document:
                    for text_block in page.get_text_blocks():
                        if '\x00' in text_block[4]:
                            continue

                        chunks.append(text_block[4].replace("\n", " "))

                num_characters_extracted = len("".join(chunks))
                if num_characters_extracted < 100:
                    print(f"Minimal text extracted for document {db_document[1]}. Falling back to OCR.")
                    chunks = []
                    for page in document:
                        pixels = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        image = Image.frombytes("RGB", [pixels.width, pixels.height], pixels.samples)
                        image = image.convert("L")
                        text = pytesseract.image_to_string(image)
                        chunks.append(text)

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