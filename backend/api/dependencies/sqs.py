from typing import Annotated

from fastapi import Depends

from shared.sqs_client import (
    SQSDocumentProcessingClient,
    get_document_processing_sqs_client,
)

SQSDocumentProcessingClientDep = Annotated[
    SQSDocumentProcessingClient, Depends(get_document_processing_sqs_client)
]
