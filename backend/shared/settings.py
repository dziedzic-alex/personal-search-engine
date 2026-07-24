import enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(enum.StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: Environment
    frontend_base_url: str
    database_url: str
    redis_url: str
    jwt_secret: str
    s3_files_thumbnails_bucket_name: str
    s3_files_thumbnails_bucket_region: str
    sqs_document_processing_queue_name: str
    sqs_document_processing_dead_letter_queue_name: str
    sqs_document_queues_region: str
    ses_from_email: str
    ses_region: str


settings = Settings()
