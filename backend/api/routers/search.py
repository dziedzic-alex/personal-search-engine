from fastapi import APIRouter
from shared.db_client import get_db_client
from shared.models.text_embedding import get_text_embedding_model
from shared.models.image_embedding import get_image_embedding_model

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/")
def search(query: str):
    query_text_embedding = get_text_embedding_model().encode(query)
    query_image_embedding = get_image_embedding_model().encode(query)

    relevant_documents = []
    with get_db_client() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, 
                LEAST(
                    MIN(document_embeddings.text_embedding <=> %s), 
                    MIN(document_embeddings.image_embedding <=> %s))
                as distance
                FROM documents
                INNER JOIN document_embeddings 
                    ON document_embeddings.document_id = documents.id
                GROUP BY documents.id
                ORDER BY distance ASC
                LIMIT 5
                """,
                (query_text_embedding, query_image_embedding)
            )
            relevant_documents = cursor.fetchall()

    response = []
    for document in relevant_documents:
        response.append({
            "name": document[0],
            "distance": document[1],
        })

    return response