from sqlalchemy import bindparam, select, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import Row

from db.models.document import Document, DocumentStatus
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES, ContentType
from shared.models.cross_encoding import get_cross_encoding_model
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def _to_document(self, row: Row) -> Document:
        return Document(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            status=DocumentStatus(row.status),
            num_attempts=row.num_attempts,
            s3_content_key=row.s3_content_key,
            s3_thumbnail_key=row.s3_thumbnail_key,
            content_type=row.content_type,
            size_bytes=row.size_bytes,
            source_created_time=row.source_created_time,
            created_time=row.created_time,
        )

    def _cross_encode_text_rows(self, query: str, text_rows) -> list[Document]:
        reranker_pairs = [
            [query, f"{row.name}\n{content}"]
            for row in text_rows
            for content in row.contents
        ]
        reranker_scores = get_cross_encoding_model().predict(reranker_pairs)

        ranked_results = []
        score_offset = 0
        for row in text_rows:
            chunk_count = len(row.contents)
            chunk_ce_scores = reranker_scores[score_offset : score_offset + chunk_count]
            average_cross_encoding_score = float(sum(chunk_ce_scores) / chunk_count)

            ranked_results.append(
                {
                    "document": self._to_document(row),
                    "cross_encoding_score": average_cross_encoding_score,
                }
            )
            score_offset += chunk_count

        ranked_results.sort(
            key=lambda result: result["cross_encoding_score"], reverse=True
        )

        ranked_results = [result["document"] for result in ranked_results]
        return ranked_results

    def get_relevant_text_documents(self, query: str, user_id: int) -> list[Document]:
        query_prefix = "Represent this sentence for searching relevant passages: "
        query_text_embedding = get_text_embedding_model().encode(query_prefix + query)
        query_image_embedding = get_image_embedding_model().encode(query)

        text_embedding_search_result = self.session.execute(
            text(
                """
            WITH topk_per_document AS (
                SELECT document_embeddings.document_id,
                document_embeddings.content,
                document_embeddings.text_embedding <=> :query_text_embedding as distance,
                ROW_NUMBER() OVER (
                    PARTITION BY document_embeddings.document_id
                    ORDER BY document_embeddings.text_embedding <=> :query_text_embedding ASC
                ) as rank
                FROM document_embeddings
                WHERE document_embeddings.text_embedding IS NOT NULL
            ),

            doc_scores AS (
                SELECT document_id, AVG(distance) as average_distance
                FROM topk_per_document
                WHERE rank <= 3
                GROUP BY document_id
            )

            SELECT
                documents.*,
                array_agg(topk_per_document.content) as contents
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                    INNER JOIN topk_per_document ON documents.id = topk_per_document.document_id AND topk_per_document.rank <= 3
                WHERE documents.user_id = :user_id
                AND documents.status = :status
                AND documents.content_type = :pdf_content_type
                GROUP BY documents.id, doc_scores.average_distance
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_text_embedding": query_text_embedding,
                "user_id": user_id,
                "status": DocumentStatus.PROCESSED.value,
                "pdf_content_type": ContentType.PDF.value,
            },
        )
        text_rows = text_embedding_search_result.all()

        image_embedding_search_result = self.session.execute(
            text(
                """
            WITH topk_per_document AS (
                SELECT document_embeddings.document_id,
                document_embeddings.image_embedding <=> :query_image_embedding as distance,
                ROW_NUMBER() OVER (
                    PARTITION BY document_embeddings.document_id
                    ORDER BY document_embeddings.image_embedding <=> :query_image_embedding ASC
                ) as rank
                FROM document_embeddings
                WHERE document_embeddings.image_embedding IS NOT NULL
            ),

            doc_scores AS (
                SELECT document_id, AVG(distance) as average_distance
                FROM topk_per_document
                WHERE rank <= 3
                GROUP BY document_id
            )

            SELECT
                documents.*
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                WHERE documents.user_id = :user_id
                AND documents.status = :status
                AND documents.content_type = :pdf_content_type
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_image_embedding": query_image_embedding,
                "user_id": user_id,
                "status": DocumentStatus.PROCESSED.value,
                "pdf_content_type": ContentType.PDF.value,
            },
        )

        image_retrieval_rows: list[Document] = [
            self._to_document(row) for row in image_embedding_search_result.all()
        ]

        ranked_results = self._cross_encode_text_rows(query, text_rows)
        seen_document_ids = set(row.id for row in text_rows)

        for document in image_retrieval_rows:
            if document.id not in seen_document_ids:
                ranked_results.append(document)

        return ranked_results

    def get_relevant_image_documents(self, query: str, user_id: int) -> list[Document]:
        query_prefix = "Represent this sentence for searching relevant passages: "
        query_text_embedding = get_text_embedding_model().encode(query_prefix + query)
        query_image_embedding = get_image_embedding_model().encode(query)

        image_embedding_search_result = self.session.execute(
            text(
                """
            WITH topk_per_document AS (
                SELECT document_embeddings.document_id,
                document_embeddings.image_embedding <=> :query_image_embedding as distance,
                ROW_NUMBER() OVER (
                    PARTITION BY document_embeddings.document_id
                    ORDER BY document_embeddings.image_embedding <=> :query_image_embedding ASC
                ) as rank
                FROM document_embeddings
                WHERE document_embeddings.image_embedding IS NOT NULL
            ),

            doc_scores AS (
                SELECT document_id, AVG(distance) as average_distance
                FROM topk_per_document
                WHERE rank <= 3
                GROUP BY document_id
            )

            SELECT
                documents.*
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                WHERE documents.user_id = :user_id
                AND documents.status = :status
                AND documents.content_type IN :content_types
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_image_embedding": query_image_embedding,
                "user_id": user_id,
                "status": DocumentStatus.PROCESSED.value,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )

        ranked_results: list[Document] = [
            self._to_document(row) for row in image_embedding_search_result.all()
        ]

        text_embedding_search_result = self.session.execute(
            text(
                """
            WITH topk_per_document AS (
                SELECT document_embeddings.document_id,
                document_embeddings.content,
                document_embeddings.text_embedding <=> :query_text_embedding as distance,
                ROW_NUMBER() OVER (
                    PARTITION BY document_embeddings.document_id
                    ORDER BY document_embeddings.text_embedding <=> :query_text_embedding ASC
                ) as rank
                FROM document_embeddings
                WHERE document_embeddings.text_embedding IS NOT NULL
            ),

            doc_scores AS (
                SELECT document_id, AVG(distance) as average_distance
                FROM topk_per_document
                WHERE rank <= 3
                GROUP BY document_id
            )

            SELECT
                documents.*,
                array_agg(topk_per_document.content) as contents
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                    INNER JOIN topk_per_document ON documents.id = topk_per_document.document_id AND topk_per_document.rank <= 3
                WHERE documents.user_id = :user_id
                AND documents.status = :status
                AND documents.content_type IN :content_types
                GROUP BY documents.id, doc_scores.average_distance
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_text_embedding": query_text_embedding,
                "user_id": user_id,
                "status": DocumentStatus.PROCESSED.value,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )
        text_rows = text_embedding_search_result.all()

        seen_document_ids = set(row.id for row in ranked_results)

        text_only_rows = [row for row in text_rows if row.id not in seen_document_ids]
        ranked_results.extend(self._cross_encode_text_rows(query, text_only_rows))

        return ranked_results

    def get_documents(self, user_id: int, query: str | None = None) -> list[Document]:
        db_query = select(Document).where(Document.user_id == user_id)

        if query:
            query = query.strip()

        if query:
            db_query = db_query.where(Document.name.ilike(f"%{query}%"))

        return self.session.scalars(db_query).all()
