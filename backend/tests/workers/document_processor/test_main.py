import pytest

from db.models.document import DocumentStatus
from shared.sqs_client import ConsumerResponse
from tests.api.factories import make_document
from workers.document_processor.main import _process_document_message


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
        "workers.document_processor.main.SessionLocal",
        return_value=session,
    )
    return session


def test_process_document_message_deletes_message_when_document_not_found(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = None

    _process_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_document_message_deletes_message_when_already_processed(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = make_document(status=DocumentStatus.PROCESSED)

    _process_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_document_message_skips_without_deleting_when_not_pending(
    document_message, mock_sqs_client, mock_main_session
):
    mock_main_session.get.return_value = make_document(status=DocumentStatus.PROCESSING)

    _process_document_message(document_message, mock_sqs_client)

    mock_sqs_client.delete_document_message.assert_not_called()


def test_process_document_message_processes_pdf_and_deletes_message(
    document_message, mock_sqs_client, mock_main_session, mocker
):
    document = make_document(status=DocumentStatus.PENDING, content_type="pdf")
    mock_main_session.get.return_value = document
    mock_process_pdf = mocker.patch(
        "workers.document_processor.main.process_pdf_document"
    )

    _process_document_message(document_message, mock_sqs_client)

    assert document.status == DocumentStatus.PROCESSED
    mock_process_pdf.assert_called_once_with(document)
    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_document_message_processes_image_and_deletes_message(
    document_message, mock_sqs_client, mock_main_session, mocker
):
    document = make_document(status=DocumentStatus.PENDING, content_type="jpeg")
    mock_main_session.get.return_value = document
    mock_process_image = mocker.patch(
        "workers.document_processor.main.process_image_document"
    )

    _process_document_message(document_message, mock_sqs_client)

    assert document.status == DocumentStatus.PROCESSED
    mock_process_image.assert_called_once_with(document)
    mock_sqs_client.delete_document_message.assert_called_once_with("receipt-1")


def test_process_document_message_rolls_back_to_pending_on_processing_failure(
    document_message, mock_sqs_client, mock_main_session, mocker
):
    document = make_document(status=DocumentStatus.PENDING, content_type="pdf")
    mock_main_session.get.return_value = document
    mocker.patch(
        "workers.document_processor.main.process_pdf_document",
        side_effect=RuntimeError("processing failed"),
    )

    _process_document_message(document_message, mock_sqs_client)

    assert document.status == DocumentStatus.PENDING
    mock_main_session.execute.assert_called()
    mock_main_session.commit.assert_called()
    mock_sqs_client.delete_document_message.assert_not_called()
