import boto3
from dataclasses import dataclass
from botocore.config import Config

from shared.content_type import ContentType, content_type_to_mime_type
from shared.settings import settings

s3_client: S3Client | None = None


def get_s3_client() -> S3Client:
    global s3_client

    if s3_client is None:
        s3_client = S3Client()

    return s3_client


class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=settings.s3_files_thumbnails_bucket_region,
            config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
        )

    def get_file(self, object_key: str) -> bytes:
        response = self.client.get_object(
            Bucket=settings.s3_files_thumbnails_bucket_name,
            Key=object_key,
        )

        return response["Body"].read()

    def persist_file(
        self, filename: str, user_id: int, file_data: bytes, content_type: ContentType
    ) -> str:
        object_key = f"{user_id}/{filename}"

        self.client.put_object(
            Bucket=settings.s3_files_thumbnails_bucket_name,
            Key=object_key,
            Body=file_data,
            ContentType=content_type_to_mime_type(content_type),
        )

        return object_key

    def delete_file(self, object_key: str) -> None:
        self.client.delete_object(
            Bucket=settings.s3_files_thumbnails_bucket_name,
            Key=object_key,
        )

    @dataclass
    class ContentDispositionConfig:
        filename: str
        disposition: str = "attachment"

    def generate_presigned_url(self, object_key: str, expires_in: int = 3600, content_disposition_config: ContentDispositionConfig | None = None) -> str:
        params = {
            "Bucket": settings.s3_files_thumbnails_bucket_name,
            "Key": object_key,
        }

        if content_disposition_config is not None:
            params["ResponseContentDisposition"] = f"{content_disposition_config.disposition}; filename=\"{content_disposition_config.filename}\""

        return self.client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires_in)
