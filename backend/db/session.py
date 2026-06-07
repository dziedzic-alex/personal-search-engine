from collections.abc import Generator

from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from shared.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def register_vector_extension(db_connection, connection_record):
    register_vector(db_connection)


def get_session() -> Generator[Session]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
