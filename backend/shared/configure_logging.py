import logging

from shared.settings import Environment, settings


def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG if settings.environment == Environment.DEV else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(funcName)s %(message)s",
    )