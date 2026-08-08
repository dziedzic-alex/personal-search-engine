from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

from shared.settings import settings

if TYPE_CHECKING:
    from mypy_boto3_ses.client import SESClient as Boto3SESClient

ses_client: SESClient | None = None


def get_ses_client() -> SESClient:
    global ses_client

    if ses_client is None:
        ses_client = SESClient()

    return ses_client


class SESClient:
    def __init__(self):
        self.client: Boto3SESClient = boto3.client(
            "ses", region_name=settings.ses_region
        )

    def send_email(
        self, subject: str, body: str, html_body: str, to_addresses: list[str]
    ) -> None:
        self.client.send_email(
            Source=settings.ses_from_email,
            Destination={"ToAddresses": to_addresses},
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Text": {
                        "Data": body,
                        "Charset": "UTF-8",
                    },
                    "Html": {
                        "Data": html_body,
                        "Charset": "UTF-8",
                    },
                },
            },
        )
