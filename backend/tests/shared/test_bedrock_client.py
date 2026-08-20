import pytest

from db.models.document import DocumentStatus
from shared.bedrock_client import BedrockClient
from shared.content_type import ContentType
from tests.api.factories import uid


@pytest.fixture
def bedrock_client(mocker):
    mocker.patch("shared.bedrock_client.boto3.client")
    client = BedrockClient()
    client.bedrock_agent_client = mocker.MagicMock()
    client.bedrock_agent_runtime_client = mocker.MagicMock()
    return client


@pytest.mark.parametrize(
    ("bedrock_status", "expected"),
    [
        ("STARTING", DocumentStatus.PENDING),
        ("PENDING", DocumentStatus.PENDING),
        ("IN_PROGRESS", DocumentStatus.PROCESSING),
        ("PARTIALLY_INDEXED", DocumentStatus.PROCESSING),
        ("INDEXED", DocumentStatus.PROCESSED),
        ("METADATA_PARTIALLY_INDEXED", DocumentStatus.PROCESSING),
        ("METADATA_UPDATE_FAILED", DocumentStatus.FAILED),
        ("FAILED", DocumentStatus.FAILED),
        ("NOT_FOUND", DocumentStatus.FAILED),
        ("IGNORED", DocumentStatus.FAILED),
        ("DELETING", DocumentStatus.FAILED),
    ],
)
def test_to_document_status_mapping(bedrock_status, expected):
    assert (
        BedrockClient._to_document_status(uid(1), bedrock_status, "reason")
        == expected
    )


def test_ingest_image_document_rejects_oversized_image(bedrock_client):
    oversized = (
        b"x"
        * (BedrockClient.MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES + 1)
    )

    with pytest.raises(ValueError, match="greater than the maximum allowed size"):
        bedrock_client.ingest_image_document(
            uid(1),
            "user@example.com",
            oversized,
            ContentType.JPEG,
        )

    bedrock_client.bedrock_agent_client.ingest_knowledge_base_documents.assert_not_called()


def test_ingest_image_document_allows_max_size(bedrock_client):
    image_data = (
        b"x" * BedrockClient.MAX_BEDROCK_INGESTION_IMAGE_DOCUMENT_SIZE_BYTES
    )
    bedrock_client.bedrock_agent_client.ingest_knowledge_base_documents.return_value = {
        "documentDetails": [{"status": "STARTING"}]
    }

    status = bedrock_client.ingest_image_document(
        uid(1),
        "user@example.com",
        image_data,
        ContentType.JPEG,
    )

    assert status == DocumentStatus.PENDING
    bedrock_client.bedrock_agent_client.ingest_knowledge_base_documents.assert_called_once()


def test_get_documents_ingestion_statuses_returns_empty_for_no_ids(bedrock_client):
    assert bedrock_client.get_documents_ingestion_statuses([]) == []
    bedrock_client.bedrock_agent_client.get_knowledge_base_documents.assert_not_called()


def test_get_documents_ingestion_statuses_batches_requests(bedrock_client):
    document_ids = [uid(i) for i in range(1, 12)]
    batch_size = BedrockClient.MAX_NUM_DOCUMENTS_PER_GET_KB_DOCUMENTS_REQUEST

    def get_knowledge_base_documents(**kwargs):
        identifiers = kwargs["documentIdentifiers"]
        return {
            "documentDetails": [
                {
                    "identifier": {"custom": {"id": identifier["custom"]["id"]}},
                    "status": "INDEXED",
                }
                for identifier in identifiers
            ]
        }

    bedrock_client.bedrock_agent_client.get_knowledge_base_documents.side_effect = (
        get_knowledge_base_documents
    )

    statuses = bedrock_client.get_documents_ingestion_statuses(document_ids)

    assert len(statuses) == 11
    assert all(status.status == DocumentStatus.PROCESSED for status in statuses)
    assert [
        status.document_id for status in statuses
    ] == document_ids

    calls = bedrock_client.bedrock_agent_client.get_knowledge_base_documents.call_args_list
    assert len(calls) == 2
    assert len(calls[0].kwargs["documentIdentifiers"]) == batch_size
    assert len(calls[1].kwargs["documentIdentifiers"]) == 1


def test_retrieve_relevant_document_chunks_skips_missing_id_or_score(bedrock_client):
    bedrock_client.bedrock_agent_runtime_client.retrieve.return_value = {
        "retrievalResults": [
            {
                "location": {"customDocumentLocation": {}},
                "score": 0.9,
            },
            {
                "location": {"customDocumentLocation": {"id": str(uid(1))}},
            },
            {
                "location": {"customDocumentLocation": {"id": str(uid(2))}},
                "score": 0.8,
            },
        ]
    }

    chunks = bedrock_client.retrieve_relevant_document_chunks(
        "query",
        "user@example.com",
    )

    assert chunks == [
        BedrockClient.RelevantDocumentChunk(document_id=uid(2), score=0.8)
    ]
    bedrock_client.bedrock_agent_runtime_client.retrieve.assert_called_once()
