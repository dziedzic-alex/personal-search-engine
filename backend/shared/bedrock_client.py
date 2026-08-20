from typing import TYPE_CHECKING

import boto3

from db.models.document import DocumentStatus
from shared.content_type import ContentType
from shared.settings import settings

if TYPE_CHECKING:
    from mypy_boto3_bedrock_agent.client import AgentsforBedrockClient
    from mypy_boto3_bedrock_agent.type_defs import MetadataAttributeTypeDef
    from mypy_boto3_bedrock_agent_runtime.client import (
        AgentsforBedrockRuntimeClient,
    )

import logging
import uuid
from dataclasses import dataclass

from shared.content_type import content_type_to_mime_type

logger = logging.getLogger(__name__)

bedrock_client: BedrockClient | None = None

def get_bedrock_client() -> BedrockClient:
    global bedrock_client

    if bedrock_client is None:
        bedrock_client = BedrockClient()

    return bedrock_client

OWNER_USER_ID_METADATA_KEY = 'owner_user_id'

def _make_user_id_metadata_attribute(user_id: uuid.UUID) -> MetadataAttributeTypeDef:
    return {
        'key': OWNER_USER_ID_METADATA_KEY,
        'value': {
            'type': 'STRING',
            'stringValue': str(user_id)
        }
    }

class BedrockClient:
    def __init__(self):
        self.bedrock_agent_client: AgentsforBedrockClient = boto3.client('bedrock-agent')
        self.bedrock_agent_runtime_client: AgentsforBedrockRuntimeClient = boto3.client('bedrock-agent-runtime')

    @staticmethod
    def _to_document_status(document_id: uuid.UUID, status: str, status_reason: str | None = None) -> DocumentStatus:
        document_status: DocumentStatus | None = None

        if status == 'STARTING':
            document_status = DocumentStatus.PENDING
        elif status == 'PENDING':
            document_status = DocumentStatus.PENDING
        elif status == 'IN_PROGRESS':
            document_status = DocumentStatus.PROCESSING
        elif status == 'PARTIALLY_INDEXED':
            document_status = DocumentStatus.PROCESSING
        elif status == 'INDEXED':
            document_status = DocumentStatus.PROCESSED
        elif status == 'METADATA_PARTIALLY_INDEXED':
            document_status = DocumentStatus.PROCESSING
        elif status == 'METADATA_UPDATE_FAILED':
            document_status = DocumentStatus.FAILED
        elif status == 'FAILED':
            document_status = DocumentStatus.FAILED
        elif status == 'NOT_FOUND':
            document_status = DocumentStatus.FAILED
        elif status == 'IGNORED':
            document_status = DocumentStatus.FAILED
        elif status == 'DELETING':
            document_status = DocumentStatus.FAILED
        else:
            document_status = DocumentStatus.FAILED

        if document_status == DocumentStatus.FAILED:
            logger.error(f"Document {document_id} ingestion failed: {status} - {status_reason if status_reason else 'No reason provided'}")

        return document_status


    def ingest_text_document(self, document_id: uuid.UUID, s3_content_key: str, user_id: uuid.UUID) -> DocumentStatus:
        response = self.bedrock_agent_client.ingest_knowledge_base_documents(
            knowledgeBaseId=settings.knowledge_base_id,
            dataSourceId=settings.knowledge_base_data_source_id,
            documents=[
                {
                    'metadata': {
                        'type': 'IN_LINE_ATTRIBUTE',
                        'inlineAttributes': [
                            _make_user_id_metadata_attribute(user_id)
                        ]
                    },
                    'content': {
                        'dataSourceType': 'CUSTOM',
                        'custom': {
                            'customDocumentIdentifier': {
                                'id': str(document_id)
                            },
                            'sourceType': 'S3_LOCATION',
                            's3Location': {
                                'uri': f's3://{settings.s3_files_thumbnails_bucket_name}/{s3_content_key}'
                            }
                        }
                    }
                }
            ]
        )

        response_document_details = response['documentDetails'][0]
        status = response_document_details['status']
        status_reason = response_document_details.get('statusReason')
        
        return self._to_document_status(document_id, status, status_reason)

    MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES = 5 * 1024 * 1024 # 5MB

    def ingest_image_document(self, document_id: uuid.UUID, user_id: uuid.UUID, image_data: bytes, content_type: ContentType) -> DocumentStatus:
        if len(image_data) > self.MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES:
            raise ValueError(f"Image data size {len(image_data)} bytes is greater than the maximum allowed size of {self.MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES} bytes")

        response = self.bedrock_agent_client.ingest_knowledge_base_documents(
            knowledgeBaseId=settings.knowledge_base_id,
            dataSourceId=settings.knowledge_base_data_source_id,
            documents=[
                {
                    'metadata': {
                        'type': 'IN_LINE_ATTRIBUTE',
                        'inlineAttributes': [
                            _make_user_id_metadata_attribute(user_id)
                        ]
                    },
                    'content': {
                        'dataSourceType': 'CUSTOM',
                        'custom': {
                            'customDocumentIdentifier': {
                                'id': str(document_id)
                            },
                            'sourceType': 'IN_LINE',
                            'inlineContent': {
                                'type': 'BYTE',
                                'byteContent': {
                                    'mimeType': content_type_to_mime_type(content_type),
                                    'data': image_data
                                }
                            }
                        }
                    }
                }
            ]
        )

        response_document_details = response['documentDetails'][0]
        status = response_document_details['status']
        status_reason = response_document_details.get('statusReason')
        
        return self._to_document_status(document_id, status, status_reason)
        
    @dataclass
    class DocumentIngestionStatus:
        document_id: uuid.UUID
        status: DocumentStatus

    MAX_NUM_DOCUMENTS_PER_GET_KB_DOCUMENTS_REQUEST = 10

    def get_documents_ingestion_statuses(self, document_ids: list[uuid.UUID]) -> list[DocumentIngestionStatus]:
        if len(document_ids) == 0:
            return []

        document_identifiers_request = []
        for document_id in document_ids:
            document_identifiers_request.append({
                'dataSourceType': 'CUSTOM',
                'custom': {
                    'id': str(document_id)
                }
            })

        ingestion_statuses = []
        for i in range(0, len(document_ids), self.MAX_NUM_DOCUMENTS_PER_GET_KB_DOCUMENTS_REQUEST):
            response = self.bedrock_agent_client.get_knowledge_base_documents(
                knowledgeBaseId=settings.knowledge_base_id,
                dataSourceId=settings.knowledge_base_data_source_id,
                documentIdentifiers=document_identifiers_request[i:i + self.MAX_NUM_DOCUMENTS_PER_GET_KB_DOCUMENTS_REQUEST]
            )

            response_documents_details = response['documentDetails']
            for response_document in response_documents_details:
                document_id = response_document['identifier'].get('custom', {}).get('id')
                status = response_document['status']
                status_reason = response_document.get('statusReason')

                if document_id is None:
                    continue

                document_id = uuid.UUID(document_id)
                ingestion_statuses.append(self.DocumentIngestionStatus(document_id=document_id, status=self._to_document_status(document_id, status, status_reason)))

        return ingestion_statuses

    MAX_NUM_DOCUMENTS_PER_DELETE_REQUEST = 10

    def delete_documents(self, document_ids: list[uuid.UUID]):
        if len(document_ids) == 0:
            return

        documents_to_delete = []
        for document_id in document_ids:
            documents_to_delete.append({
                'dataSourceType': 'CUSTOM',
                'custom': {
                    'id': str(document_id)
                }
            })

        for i in range(0, len(documents_to_delete), self.MAX_NUM_DOCUMENTS_PER_DELETE_REQUEST):
            self.bedrock_agent_client.delete_knowledge_base_documents(
                knowledgeBaseId=settings.knowledge_base_id,
                dataSourceId=settings.knowledge_base_data_source_id,
                documentIdentifiers=documents_to_delete[i:i + self.MAX_NUM_DOCUMENTS_PER_DELETE_REQUEST]
            )

    @dataclass
    class RelevantDocumentChunk:
        document_id: uuid.UUID
        score: float

    def retrieve_relevant_document_chunks(self, query: str, user_id: uuid.UUID) -> list[RelevantDocumentChunk]:
        response = self.bedrock_agent_runtime_client.retrieve(
            knowledgeBaseId=settings.knowledge_base_id,
            retrievalQuery={
                'type': 'TEXT',
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 50,
                    'filter': {
                        'equals': {
                            'key': OWNER_USER_ID_METADATA_KEY,
                            'value': str(user_id) # type: ignore - correct according to AWS documentation
                        }
                    }
                }
            }
        )

        retrieval_results = response['retrievalResults']
        relevant_chunks = []

        for retrieval_result in retrieval_results:
            document_id = retrieval_result.get('location', {}).get('customDocumentLocation', {}).get('id')
            score = retrieval_result.get('score')

            if document_id is None or score is None:
                continue

            relevant_chunks.append(self.RelevantDocumentChunk(
                document_id=uuid.UUID(document_id),
                score=float(score)
            ))

        return relevant_chunks
    