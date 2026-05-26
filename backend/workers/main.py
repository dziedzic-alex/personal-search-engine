from shared.redis_client import get_redis_client
from pathlib import Path
import json
import fitz

def main():
    print('Worker is running')

    redis_client = get_redis_client()

    while True:
        job = redis_client.brpop("jobs:upload", timeout=5)

        if not job:
            continue

        queue_name, job_data = job
        job_data = json.loads(job_data)

        print(f"Processing job: {job_data}")

        file_path = Path(job_data['path'])
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        document: fitz.Document = fitz.open(file_path)
        chunks: list[str] = []
        for page in document:
            for text_block in page.get_text_blocks():
                chunks.append(text_block[4].replace("\n", " "))

        print(f"Chunks: {chunks}")


if __name__ == "__main__":
    main()