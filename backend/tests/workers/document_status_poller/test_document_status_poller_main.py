import pytest
from sqlalchemy.sql.dml import Update

from db.models.document import DocumentStatus
from shared.bedrock_client import BedrockClient
from tests.api.factories import make_document, uid
from workers.document_status_poller.main import poll_document_statuses


@pytest.fixture
def mock_bedrock_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_main_session(mocker):
    session = mocker.MagicMock()
    session.__enter__ = mocker.Mock(return_value=session)
    session.__exit__ = mocker.Mock(return_value=False)
    mocker.patch(
        "workers.document_status_poller.main.SessionLocal",
        return_value=session,
    )
    return session


def test_poll_document_statuses_noop_when_no_documents(
    mock_bedrock_client, mock_main_session
):
    mock_main_session.scalars.return_value.all.return_value = []
    mock_bedrock_client.get_documents_ingestion_statuses.return_value = []

    poll_document_statuses(mock_bedrock_client)

    mock_bedrock_client.get_documents_ingestion_statuses.assert_called_once_with([])
    mock_main_session.execute.assert_not_called()
    mock_main_session.commit.assert_not_called()


def test_poll_document_statuses_noop_when_bedrock_returns_no_statuses(
    mock_bedrock_client, mock_main_session
):
    documents = [
        make_document(id=uid(1), status=DocumentStatus.PENDING),
        make_document(id=uid(2), status=DocumentStatus.PROCESSING),
    ]
    mock_main_session.scalars.return_value.all.return_value = documents
    mock_bedrock_client.get_documents_ingestion_statuses.return_value = []

    poll_document_statuses(mock_bedrock_client)

    mock_bedrock_client.get_documents_ingestion_statuses.assert_called_once_with(
        [uid(1), uid(2)]
    )
    mock_main_session.execute.assert_not_called()
    mock_main_session.commit.assert_not_called()


def test_poll_document_statuses_updates_non_pending_statuses(
    mock_bedrock_client, mock_main_session
):
    documents = [
        make_document(id=uid(1), status=DocumentStatus.PENDING),
        make_document(id=uid(2), status=DocumentStatus.PROCESSING),
        make_document(id=uid(3), status=DocumentStatus.PROCESSING),
    ]
    mock_main_session.scalars.return_value.all.return_value = documents
    mock_bedrock_client.get_documents_ingestion_statuses.return_value = [
        BedrockClient.DocumentIngestionStatus(
            document_id=uid(1), status=DocumentStatus.PENDING
        ),
        BedrockClient.DocumentIngestionStatus(
            document_id=uid(2), status=DocumentStatus.PROCESSED
        ),
        BedrockClient.DocumentIngestionStatus(
            document_id=uid(3), status=DocumentStatus.FAILED
        ),
    ]

    poll_document_statuses(mock_bedrock_client)

    assert mock_main_session.execute.call_count == 2
    for call in mock_main_session.execute.call_args_list:
        assert isinstance(call.args[0], Update)
    mock_main_session.commit.assert_called_once()


def test_poll_document_statuses_skips_updates_when_all_still_pending(
    mock_bedrock_client, mock_main_session
):
    documents = [make_document(id=uid(1), status=DocumentStatus.PENDING)]
    mock_main_session.scalars.return_value.all.return_value = documents
    mock_bedrock_client.get_documents_ingestion_statuses.return_value = [
        BedrockClient.DocumentIngestionStatus(
            document_id=uid(1), status=DocumentStatus.PENDING
        ),
    ]

    poll_document_statuses(mock_bedrock_client)

    mock_main_session.execute.assert_not_called()
    mock_main_session.commit.assert_called_once()


def test_poll_document_statuses_swallows_errors(mock_bedrock_client, mock_main_session):
    mock_main_session.scalars.side_effect = Exception("db error")

    poll_document_statuses(mock_bedrock_client)

    mock_bedrock_client.get_documents_ingestion_statuses.assert_not_called()
    mock_main_session.commit.assert_not_called()
