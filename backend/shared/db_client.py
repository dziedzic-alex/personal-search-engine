import os
import psycopg
from pgvector.psycopg import register_vector

def get_db_client() -> psycopg.Connection:
    connection = psycopg.connect(os.getenv("DATABASE_URL"))
    register_vector(connection)
    return connection