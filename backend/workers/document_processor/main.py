from pillow_heif import register_heif_opener
from sqlalchemy import delete

from db.models.document import Document, DocumentStatus
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES, ContentType
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.s3_client import get_s3_client
from shared.sqs_client import ConsumerResponse, SQSDocumentProcessingClient, get_document_processing_sqs_client
from workers.document_processor.image.image import process_image_document
from workers.document_processor.pdf.pdf import process_pdf_document

register_heif_opener()


def main():
    print("Worker is running")

    get_text_embedding_model()
    get_image_embedding_model()
    get_s3_client()

    sqs_client = get_document_processing_sqs_client()

    print("Models and clients initialized")

    while True:
        try:
            document_message = sqs_client.get_document_message()

            if document_message is None:
                continue

            _process_document_message(document_message, sqs_client)
        except Exception as e:
            print(f"Worker error: {e}")
            continue


def _process_document_message(document_message: ConsumerResponse, sqs_client: SQSDocumentProcessingClient) -> None:
    print(f"Processing document: {document_message.document_id}")

    with SessionLocal(expire_on_commit=False) as session:
        document: Document | None = session.get(Document, document_message.document_id)

        if document is None:
            print(f"Document {document_message.document_id} not found. Skipping...")
            sqs_client.delete_document_message(document_message.receipt_handle)
            return

        if document.status == DocumentStatus.PROCESSED:
            print(f"Document {document.name} already processed. Skipping...")
            sqs_client.delete_document_message(document_message.receipt_handle)
            return
        elif document.status != DocumentStatus.PENDING:
            print(
                f"Document {document.name} is not pending. Skipping..."
            )
            return

        document.status = DocumentStatus.PROCESSING
        session.commit()

    try:
        if document.content_type in IMAGE_CONTENT_TYPE_VALUES:
            process_image_document(document)
        elif document.content_type == ContentType.PDF.value:
            process_pdf_document(document)
        else:
            raise ValueError(f"Unsupported document type: {document.content_type}")
    except Exception as e:
        print(f"Error processing document {document.name}: {e}")

        with SessionLocal() as session:
            document = session.get(Document, document_message.document_id)
            document.status = DocumentStatus.PENDING
            session.execute(delete(DocumentEmbedding).where(DocumentEmbedding.document_id == document.id))
            session.commit()

        return

    with SessionLocal(expire_on_commit=False) as session:
        document = session.get(Document, document_message.document_id)
        document.status = DocumentStatus.PROCESSED
        session.commit()

    print(f"Document {document.name} successfully processed")
    sqs_client.delete_document_message(document_message.receipt_handle)




if __name__ == "__main__":
    main()
