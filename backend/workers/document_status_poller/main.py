import logging
import uuid
from collections import defaultdict
from time import sleep

from sqlalchemy import select, update

from db.models.document import Document, DocumentStatus
from db.session import SessionLocal
from shared.bedrock_client import BedrockClient, get_bedrock_client
from shared.configure_logging import configure_logging
from shared.settings import settings

configure_logging()

logger = logging.getLogger(__name__)


def main():
    if not settings.is_document_processing_v2_enabled:
        logger.info("Document processing v2 is not enabled. Exiting...")
        exit(0)

    logger.info("Document status poller is running")

    bedrock_client = get_bedrock_client()

    while True:
        poll_document_statuses(bedrock_client)
        sleep(30)

def poll_document_statuses(bedrock_client: BedrockClient):
    try:
        with SessionLocal() as session:
            documents_to_poll = session.scalars(select(Document).where(Document.status.in_([DocumentStatus.PENDING, DocumentStatus.PROCESSING]))).all()

        document_ids_to_poll = [document.id for document in documents_to_poll]
        document_ingestion_statuses = bedrock_client.get_documents_ingestion_statuses(document_ids_to_poll)

        if len(document_ingestion_statuses) == 0:
            return

        status_to_ids = defaultdict[DocumentStatus, list[uuid.UUID]](list)
        for ingestion_status in document_ingestion_statuses:
            if ingestion_status.status == DocumentStatus.PENDING:
                continue
            
            status_to_ids[ingestion_status.status].append(ingestion_status.document_id)

        with SessionLocal() as session:
            for status, ids in status_to_ids.items():
                session.execute(update(Document).where(Document.id.in_(ids)).values(status=status))

            session.commit()
    except Exception:
        logger.error("Error polling & updating document statuses", exc_info=True)
        pass

if __name__ == "__main__":
    main()