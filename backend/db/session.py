import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from collections.abc import Generator
from sqlalchemy import event
from pgvector.psycopg import register_vector

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def register_vector_extension(db_connection, connection_record):
    register_vector(db_connection)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
