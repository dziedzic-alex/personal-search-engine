from shared.sqs_client import get_document_processing_dead_letter_sqs_client
from db.session import SessionLocal
from db.models.document import Document, DocumentStatus

def main():
    print("Failed document watcher is running")

    sqs_client = get_document_processing_dead_letter_sqs_client()

    while True:
        try:
            document_message = sqs_client.get_document_message()

            if document_message is None:
                continue

            with SessionLocal() as session:
                document = session.get(Document, document_message.document_id)

                if document is None:
                    print(f"Document {document_message.document_id} not found. Skipping...")
                    sqs_client.delete_document_message(document_message.receipt_handle)
                    continue

                if document.status == DocumentStatus.FAILED:
                    print(f"Document {document_message.document_id} already marked as failed. Skipping...")
                    sqs_client.delete_document_message(document_message.receipt_handle)
                    continue
                elif document.status == DocumentStatus.PROCESSED:
                    print(f"Document {document_message.document_id} already processed. Skipping...")
                    sqs_client.delete_document_message(document_message.receipt_handle)
                    continue

                document.status = DocumentStatus.FAILED
                session.commit()
            
            sqs_client.delete_document_message(document_message.receipt_handle)
        except Exception as e:
            print(f"Error marking document as failed: {e}")
            continue


if __name__ == "__main__":
    main()