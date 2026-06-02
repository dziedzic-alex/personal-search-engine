from sqlalchemy import Row, text
from sqlalchemy.orm import Session

from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_relevant_documents(self, query: str) -> list[Row]:
        query_text_embedding = get_text_embedding_model().encode(query)
        query_image_embedding = get_image_embedding_model().encode(query)

        result = self.session.execute(
            text(
                """
            SELECT name, 
            LEAST(
                MIN(document_embeddings.text_embedding <=> :query_text_embedding), 
                MIN(document_embeddings.image_embedding <=> :query_image_embedding))
            as distance
            FROM documents
            INNER JOIN document_embeddings 
                ON document_embeddings.document_id = documents.id
            GROUP BY documents.id
            ORDER BY distance ASC
            LIMIT 5
            """
            ),
            {
                "query_text_embedding": query_text_embedding,
                "query_image_embedding": query_image_embedding,
            },
        )
        relevant_documents = result.all()

        return relevant_documents
