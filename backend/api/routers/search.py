from fastapi import APIRouter
from shared.db_client import get_db_client
from sentence_transformers import SentenceTransformer

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
def search(query: str):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query)

    relevant_documents = []
    with get_db_client() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, MIN(chunks.embedding <=> %s) as distance
                FROM documents
                INNER JOIN chunks 
                    ON chunks.document_id = documents.id
                GROUP BY documents.id
                ORDER BY distance ASC
                LIMIT 5
                """,
                (query_embedding,)
            )
            relevant_documents = cursor.fetchall()

    print(relevant_documents)

    response = []
    for document in relevant_documents:
        response.append({
            "name": document[0],
            "distance": document[1],
        })

    return response