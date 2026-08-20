import logging

from db.models.document import Document, DocumentStatus
from db.session import SessionLocal
from shared.configure_logging import configure_logging
from shared.settings import settings
from shared.sqs_client import (
    ConsumerResponse,
    SQSDocumentProcessingDeadLetterClient,
    get_document_processing_dead_letter_sqs_client,
)

configure_logging()

logger = logging.getLogger(__name__)


def main():
    if settings.is_document_processing_v2_enabled:
        logger.info("Document processing v2 is enabled. Exiting...")
        exit(0)

    logger.info("Failed document watcher is running")

    sqs_client = get_document_processing_dead_letter_sqs_client()

    while True:
        try:
            document_message = sqs_client.get_document_message()

            if document_message is None:
                continue

            _process_failed_document_message(document_message, sqs_client)
        except Exception:
            logger.error("Worker error", exc_info=True)
            continue


def _process_failed_document_message(
    document_message: ConsumerResponse,
    sqs_client: SQSDocumentProcessingDeadLetterClient,
) -> None:
    with SessionLocal() as session:
        document = session.get(Document, document_message.document_id)

        if document is None:
            logger.warning(
                f"Document {document_message.document_id} not found. Skipping..."
            )
            sqs_client.delete_document_message(document_message.receipt_handle)
            return

        if document.status == DocumentStatus.FAILED:
            logger.warning(
                f"Document {document_message.document_id} already marked as failed. Skipping..."
            )
            sqs_client.delete_document_message(document_message.receipt_handle)
            return
        elif document.status == DocumentStatus.PROCESSED:
            logger.warning(
                f"Document {document_message.document_id} already processed. Skipping..."
            )
            sqs_client.delete_document_message(document_message.receipt_handle)
            return

        document.status = DocumentStatus.FAILED
        session.commit()

    sqs_client.delete_document_message(document_message.receipt_handle)


if __name__ == "__main__":
    main()
