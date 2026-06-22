import enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(enum.StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    environment: Environment
    database_url: str
    redis_url: str
    jwt_secret: str
    s3_files_thumbnails_bucket_name: str
    s3_files_thumbnails_bucket_region: str
    jwt_algorithm: str = "HS256"
    access_token_expires_in_minutes: int = 5
    refresh_token_expires_in_days: int = 7


settings = Settings()
