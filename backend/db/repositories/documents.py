from sqlalchemy import Row, bindparam, text
from sqlalchemy.orm import Session

from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.models.cross_encoding import get_cross_encoding_model
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES

class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_relevant_text_documents(self, query: str) -> list[Row]:
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
                WHERE documents.content_type = 'pdf'
                GROUP BY documents.id, doc_scores.average_distance
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_text_embedding": query_text_embedding,
            },
        )
        most_relevant_text_documents = text_embedding_search_result.all()

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
                WHERE documents.content_type = 'pdf'
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ),
            {
                "query_image_embedding": query_image_embedding,
            },
        )

        most_relevant_image_embedding_per_document = image_embedding_search_result.all()


        cross_encoding_pairs = [[query, f"{document.name}\n{content}"] for document in most_relevant_text_documents for content in document.contents]
        cross_encoding_scores = get_cross_encoding_model().predict(cross_encoding_pairs)

        seen_document_ids = set()
        most_relevant_documents = []
        offset = 0
        for document in most_relevant_text_documents:
            document_id, name, content_url, thumbnail_url, average_distance, contents = document
            num_embeddings_for_document = len(contents)
            seen_document_ids.add(document_id)
           
            cross_encoding_scores_for_document = cross_encoding_scores[offset:offset + num_embeddings_for_document]
            average_cross_encoding_score = sum(cross_encoding_scores_for_document) / len(cross_encoding_scores_for_document)

            relevant_document = [document_id, name, content_url, thumbnail_url, average_distance, float(average_cross_encoding_score)]
            most_relevant_documents.append(relevant_document)

            offset += num_embeddings_for_document

        most_relevant_documents = sorted(most_relevant_documents, key=lambda x: x[5], reverse=True)

        for image_document in most_relevant_image_embedding_per_document:
            if image_document.id not in seen_document_ids:
                most_relevant_documents.append([image_document.id, image_document.name, image_document.content_url, image_document.thumbnail_url, float(image_document.average_distance), 'no cross encoding image'])

        return most_relevant_documents

    def get_relevant_image_documents(self, query: str) -> list[Row]:
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
                WHERE documents.content_type IN :content_types
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_image_embedding": query_image_embedding,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )

        most_relevant_image_embedding_per_document = image_embedding_search_result.all()

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
                topk_per_document.content
                FROM documents
                    INNER JOIN doc_scores ON documents.id = doc_scores.document_id
                    INNER JOIN topk_per_document ON documents.id = topk_per_document.document_id AND topk_per_document.rank = 1
                WHERE documents.content_type IN :content_types
                ORDER BY doc_scores.average_distance ASC
                LIMIT 20
            """
            ).bindparams(bindparam("content_types", expanding=True)),
            {
                "query_text_embedding": query_text_embedding,
                "content_types": list(IMAGE_CONTENT_TYPE_VALUES),
            },
        )
        most_relevant_text_embedding_per_document = text_embedding_search_result.all()

        cross_encoding_scores = get_cross_encoding_model().predict([[query, f"{text_document.name}\n{text_document.content}"] for text_document in most_relevant_text_embedding_per_document])
        most_relevant_text_embedding_per_document = zip(most_relevant_text_embedding_per_document, cross_encoding_scores)
        most_relevant_text_embedding_per_document = sorted(most_relevant_text_embedding_per_document, key=lambda x: x[1], reverse=True)

        document_ids_in_list = set()
        final_text_image_document_rankings = []
        for image_document in most_relevant_image_embedding_per_document:
            document_ids_in_list.add(image_document.id)
            final_text_image_document_rankings.append([image_document, float(image_document.average_distance)])

        for text_document, cross_encoding_score in most_relevant_text_embedding_per_document:
            if text_document.id not in document_ids_in_list:
                document_ids_in_list.add(text_document.id)
                final_text_image_document_rankings.append([text_document, float(cross_encoding_score)])


        return final_text_image_document_rankings

        
