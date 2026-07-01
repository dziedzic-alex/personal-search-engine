import pytest

from db.models.document import DocumentStatus
from shared.sqs_client import ConsumerResponse
from tests.api.factories import make_document
from workers.failed_document_watcher.main import _process_failed_document_message


@pytest.fixture
def document_message():
    return ConsumerResponse(document_id=1, receipt_handle="receipt-1")


@pytest.fixture
def mock_sqs_client(mocker):
    return mocker.MagicMock()


@pytest.fixture
def mock_main_session(mocker):
    session = mocker.MagicMock()
    session.__enter__ = mocker.Mock(return_value=session)
    session.__exit__ = mocker.Mock(return_value=False)
    mocker.patch(
        "workers.failed_document_watcher.main.SessionLocal",
        return_value=session,
    )
    return session


def test_process_failed_document_message_deletes_message_when_document_not_found(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = None

    _process_failed_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_failed_document_message_deletes_message_when_already_failed(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = make_document(status=DocumentStatus.FAILED)

    _process_failed_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_failed_document_message_deletes_message_when_already_processed(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = make_document(status=DocumentStatus.PROCESSED)

    _process_failed_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_failed_document_message_marks_pending_document_as_failed(
    document_message, mock_sqs_client, mock_main_session
):
    document = make_document(status=DocumentStatus.PENDING)
    mock_main_session.get.return_value = document

    _process_failed_document_message(document_message, mock_sqs_client)

    assert document.status == DocumentStatus.FAILED
    mock_main_session.commit.assert_called_once()
    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_failed_document_message_marks_processing_document_as_failed(
    document_message, mock_sqs_client, mock_main_session
):
    document = make_document(status=DocumentStatus.PROCESSING)
    mock_main_session.get.return_value = document

    _process_failed_document_message(document_message, mock_sqs_client)

    assert document.status == DocumentStatus.FAILED
    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")
