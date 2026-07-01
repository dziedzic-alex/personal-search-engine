from pillow_heif import register_heif_opener
from sqlalchemy import delete

from db.models.document import Document, DocumentStatus
from db.models.document_embedding import DocumentEmbedding
from db.session import SessionLocal
from shared.content_type import IMAGE_CONTENT_TYPE_VALUES, ContentType
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.s3_client import get_s3_client
from shared.sqs_client import get_document_processing_sqs_client
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
            document_for_processing = sqs_client.get_document_message()

            if document_for_processing is None:
                continue

            print(f"Processing document: {document_for_processing.document_id}")

            with SessionLocal(expire_on_commit=False) as session:
                document: Document | None = session.get(Document, document_for_processing.document_id)

                if document is None:
                    print(f"Document {document_for_processing.document_id} not found. Skipping...")
                    sqs_client.delete_document_message(document_for_processing.receipt_handle)
                    continue

                if document.status == DocumentStatus.PROCESSED:
                    print(f"Document {document.name} already processed. Skipping...")
                    sqs_client.delete_document_message(document_for_processing.receipt_handle)
                    continue
                elif document.status != DocumentStatus.PENDING:
                    print(
                        f"Document {document.name} is not pending. Skipping..."
                    )
                    continue

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
                    document = session.get(Document, document_for_processing.document_id)
                    document.status = DocumentStatus.PENDING
                    session.execute(delete(DocumentEmbedding).where(DocumentEmbedding.document_id == document.id))
                    session.commit()

                continue

            with SessionLocal(expire_on_commit=False) as session:
                document = session.get(Document, document_for_processing.document_id)
                document.status = DocumentStatus.PROCESSED
                session.commit()

            print(f"Document {document.name} successfully processed")
            sqs_client.delete_document_message(document_for_processing.receipt_handle)
        except Exception as e:
            print(f"Worker error: {e}")
            continue



if __name__ == "__main__":
    main()
