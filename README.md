# Personal Search Engine

**Work in progress** — a self-hosted semantic search tool for personal documents and photos. Upload PDFs and images, index them with embedding models, and search by natural language.

## What it does

- Upload PDFs and images (JPEG, PNG, WebP, HEIC/HEIF)
- Process files asynchronously in a background worker
- Index content with dual embeddings:
  - **Text** — [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for document text and OCR
  - **Images** — [CLIP ViT-B-32](https://huggingface.co/sentence-transformers/clip-ViT-B-32) for visual similarity
- Search across everything with a single natural-language query

Example: upload a vacation photo of you on a hike and a PDF of one of your college transcripts, then search `"me hiking on vacation in Seattle"` to find the photo or `"grades"` to find the transcript.

## Architecture

| Layer | Stack |
|-------|-------|
| Frontend | React, TypeScript, Vite, React Router, Vitest |
| API | FastAPI, SQLAlchemy, Alembic |
| Search | pgvector, Sentence Transformers |
| Queue | Redis |
| PDF parsing | PyMuPDF |
| OCR | Tesseract |
| Infra | Docker Compose |

## Getting started

### Prerequisites

- Docker & Docker Compose
- Node.js 24+ (for the frontend)

### Backend

From the `backend/` directory:

```bash
docker compose up --build --watch
```

This starts Postgres, Redis, the API, and the worker. Database migrations run automatically via a one-shot migrate service — no manual Alembic step needed, including on a fresh volume.

The API runs at http://localhost:8000.

>Note: First startup downloads embedding models (~hundreds of MB) and may take a few minutes.

To watch the worker process files:
`docker compose logs worker -f`

### Frontend
From the frontend/ directory:
```
npm install
npm run dev
```
The UI runs at http://localhost:5173 and proxies API requests to the backend.

### Try it
1. Go to Upload and submit a PDF or image
2. Wait for the worker to finish processing (check logs above)
3. Go to Search and run a query

### Project Structure
```
├── backend/
│   ├── api/           # FastAPI routes (upload, search)
│   ├── db/            # SQLAlchemy models, Alembic migrations
│   ├── workers/       # Background PDF/image processing
│   ├── shared/        # Embedding models, Redis client
│   └── compose.yaml   # Docker services (db, redis, migrate, api, worker)
└── frontend/
    └── src/
        ├── Upload/    # File upload UI + validation utils
        └── Search/    # Search UI
```

### Development
```
# Frontend
cd frontend
npm run lint
npm run dev
npm run build
npm run test:run

# Backend (inside the api container or locally with deps installed)
cd backend
ruff check .
ruff check --fix .
ruff format --check .
ruff format .
docker compose up --build --watch
docker compose down
docker compose down -v
docker compose logs worker -f
```

