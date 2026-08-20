import logging

from shared.settings import Environment, settings


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG
        if settings.environment == Environment.DEV
        else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(funcName)s %(message)s",
    )

    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("filelock").setLevel(logging.WARNING)
    logging.getLogger("python_multipart").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
