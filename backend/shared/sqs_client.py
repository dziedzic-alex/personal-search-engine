import json
from dataclasses import dataclass

import boto3

from shared.settings import settings

document_processing_sqs_client: SQSDocumentProcessingClient | None = None
document_processing_dead_letter_sqs_client: (
    SQSDocumentProcessingDeadLetterClient | None
) = None


def get_document_processing_sqs_client() -> SQSDocumentProcessingClient:
    global document_processing_sqs_client

    if document_processing_sqs_client is None:
        document_processing_sqs_client = SQSDocumentProcessingClient()

    return document_processing_sqs_client


def get_document_processing_dead_letter_sqs_client() -> (
    SQSDocumentProcessingDeadLetterClient
):
    global document_processing_dead_letter_sqs_client

    if document_processing_dead_letter_sqs_client is None:
        document_processing_dead_letter_sqs_client = (
            SQSDocumentProcessingDeadLetterClient()
        )

    return document_processing_dead_letter_sqs_client


@dataclass
class ConsumerResponse:
    document_id: int
    receipt_handle: str


class _SQSClient:
    def __init__(self, queue_name: str):
        self.client = boto3.resource(
            "sqs", region_name=settings.sqs_document_queues_region
        ).get_queue_by_name(QueueName=queue_name)

    def get_document_message(self) -> ConsumerResponse | None:
        messages = self.client.receive_messages(MaxNumberOfMessages=1)

        if not messages:
            return None

        message = messages[0]
        document_id = int(json.loads(message.body)["document_id"])
        receipt_handle = message.receipt_handle

        return ConsumerResponse(document_id=document_id, receipt_handle=receipt_handle)

    def delete_document_message(self, receipt_handle: str) -> None:
        self.client.delete_messages(
            Entries=[{"Id": "1", "ReceiptHandle": receipt_handle}]
        )


class SQSDocumentProcessingClient(_SQSClient):
    def __init__(self):
        super().__init__(settings.sqs_document_processing_queue_name)

    def submit_document_message(self, document_id: int, user_id: int) -> None:
        self.client.send_message(
            MessageBody=json.dumps({"document_id": document_id}),
            MessageGroupId=str(user_id),
        )


class SQSDocumentProcessingDeadLetterClient(_SQSClient):
    def __init__(self):
        super().__init__(settings.sqs_document_processing_dead_letter_queue_name)
