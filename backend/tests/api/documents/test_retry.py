import json

from db.models.document import MAX_NUM_ATTEMPTS, DocumentStatus
from tests.api.factories import make_document


def test_retry_document_requeues_processing(documents_client):
    client, mock_session, mock_redis, _, _ = documents_client
    document = make_document(status=DocumentStatus.FAILED, num_attempts=1)
    mock_session.get.return_value = document

    response = client.post("/documents/1/retry")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert document.status == DocumentStatus.PENDING
    mock_session.commit.assert_called_once()
    mock_redis.lpush.assert_called_once_with(
        "jobs:upload", json.dumps({"document_id": 1})
    )


def test_retry_document_returns_400_at_max_attempts(documents_client):
    client, mock_session, _, _, _ = documents_client
    mock_session.get.return_value = make_document(
        status=DocumentStatus.FAILED,
        num_attempts=MAX_NUM_ATTEMPTS,
    )

    response = client.post("/documents/1/retry")

    assert response.status_code == 400
