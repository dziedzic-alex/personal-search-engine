from db.models.document import Document, DocumentStatus
from db.session import SessionLocal
from shared.sqs_client import (
    ConsumerResponse,
    SQSDocumentProcessingDeadLetterClient,
    get_document_processing_dead_letter_sqs_client,
)


def main():
    print("Failed document watcher is running")

    sqs_client = get_document_processing_dead_letter_sqs_client()

    while True:
        try:
            document_message = sqs_client.get_document_message()

            if document_message is None:
                continue

            _process_failed_document_message(document_message, sqs_client)
        except Exception as e:
            print(f"Worker error: {e}")
            continue


def _process_failed_document_message(
    document_message: ConsumerResponse,
    sqs_client: SQSDocumentProcessingDeadLetterClient,
) -> None:
    with SessionLocal() as session:
        document = session.get(Document, document_message.document_id)

        if document is None:
            print(f"Document {document_message.document_id} not found. Skipping...")
            sqs_client.delete_document_message(document_message.receipt_handle)
            return

        if document.status == DocumentStatus.FAILED:
            print(
                f"Document {document_message.document_id} already marked as failed. Skipping..."
            )
            sqs_client.delete_document_message(document_message.receipt_handle)
            return
        elif document.status == DocumentStatus.PROCESSED:
            print(
                f"Document {document_message.document_id} already processed. Skipping..."
            )
            sqs_client.delete_document_message(document_message.receipt_handle)
            return

        document.status = DocumentStatus.FAILED
        session.commit()

    sqs_client.delete_document_message(document_message.receipt_handle)


if __name__ == "__main__":
    main()
