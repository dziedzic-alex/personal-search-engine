from typing import NamedTuple

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from shared.content_type import ContentType, IMAGE_CONTENT_TYPE_VALUES
from shared.models import DocumentStatus
from shared.models.cross_encoding import get_cross_encoding_model
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model


class SearchResult(NamedTuple):
    name: str
    content_url: str
    thumbnail_url: str
    average_distance: float
    cross_encoding_score: float | None


class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def _cross_encode_text_rows(self, query: str, text_rows) -> list[SearchResult]:
        reranker_pairs = [
            [query, f"{row.name}\n{content}"]
            for row in text_rows
            for content in row.contents
        ]
        reranker_scores = get_cross_encoding_model().predict(reranker_pairs)

        ranked_results: list[SearchResult] = []
        score_offset = 0
        for row in text_rows:
            chunk_count = len(row.contents)
            chunk_ce_scores = reranker_scores[score_offset : score_offset + chunk_count]
            average_cross_encoding_score = float(sum(chunk_ce_scores) / chunk_count)

            ranked_results.append(
                SearchResult(
                    name=row.name,
                    content_url=row.content_url,
                    thumbnail_url=row.thumbnail_url,
                    average_distance=float(row.average_distance),
                    cross_encoding_score=average_cross_encoding_score,
                )
            )
            score_offset += chunk_count

        ranked_results.sort(
            key=lambda result: result.cross_encoding_score, reverse=True
        )
        return ranked_results

    def get_relevant_text_documents(self, query: str, user_id: int) -> list[SearchResult]:
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
                documents.id,
                documents.name,
                documents.content_url,
                documents.thumbnail_url,
                doc_scores.average_distance,
                array_agg(topk_per_document.content) as contents
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                    INNER JOIN topk_per_document ON documents.id = topk_per_document.document_id AND topk_per_document.rank <= 3
                WHERE documents.user_id = :user_id
                AND documents.status = :completed_status
                AND documents.content_type = :pdf_content_type
                GROUP BY documents.id, doc_scores.average_distance
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_text_embedding": query_text_embedding,
                "user_id": user_id,
                "completed_status": DocumentStatus.COMPLETED.value,
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
                documents.id,
                documents.name,
                documents.content_url,
                documents.thumbnail_url,
                doc_scores.average_distance
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                WHERE documents.user_id = :user_id
                AND documents.status = :completed_status
                AND documents.content_type = :pdf_content_type
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_image_embedding": query_image_embedding,
                "user_id": user_id,
                "completed_status": DocumentStatus.COMPLETED.value,
                "pdf_content_type": ContentType.PDF.value,
            },
        )

        image_retrieval_rows = image_embedding_search_result.all()

        ranked_results = self._cross_encode_text_rows(query, text_rows)
        seen_document_ids = {row.id for row in text_rows}

        for row in image_retrieval_rows:
            if row.id not in seen_document_ids:
                ranked_results.append(
                    SearchResult(
                        name=row.name,
                        content_url=row.content_url,
                        thumbnail_url=row.thumbnail_url,
                        average_distance=float(row.average_distance),
                        cross_encoding_score=None,
                    )
                )

        return ranked_results

    def get_relevant_image_documents(self, query: str, user_id: int) -> list[SearchResult]:
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
                documents.id,
                documents.name,
                documents.content_url,
                documents.thumbnail_url,
                doc_scores.average_distance
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                WHERE documents.user_id = :user_id
                AND documents.status = :completed_status
                AND documents.content_type IN :content_types
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_image_embedding": query_image_embedding,
                "user_id": user_id,
                "completed_status": DocumentStatus.COMPLETED.value,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )

        image_retrieval_rows = image_embedding_search_result.all()

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
                documents.id,
                documents.name,
                documents.content_url,
                documents.thumbnail_url,
                doc_scores.average_distance,
                array_agg(topk_per_document.content) as contents
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                    INNER JOIN topk_per_document ON documents.id = topk_per_document.document_id AND topk_per_document.rank <= 3
                WHERE documents.user_id = :user_id
                AND documents.status = :completed_status
                AND documents.content_type IN :content_types
                GROUP BY documents.id, doc_scores.average_distance
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_text_embedding": query_text_embedding,
                "user_id": user_id,
                "completed_status": DocumentStatus.COMPLETED.value,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )
        text_rows = text_embedding_search_result.all()

        seen_document_ids = set()
        ranked_results: list[SearchResult] = []
        for row in image_retrieval_rows:
            seen_document_ids.add(row.id)
            ranked_results.append(
                SearchResult(
                    name=row.name,
                    content_url=row.content_url,
                    thumbnail_url=row.thumbnail_url,
                    average_distance=float(row.average_distance),
                    cross_encoding_score=None,
                )
            )

        text_only_rows = [row for row in text_rows if row.id not in seen_document_ids]
        ranked_results.extend(self._cross_encode_text_rows(query, text_only_rows))

        return ranked_results
