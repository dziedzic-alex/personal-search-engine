CREATE EXTENSION vector;

CREATE type document_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status document_status NOT NULL DEFAULT 'pending',
    content_url VARCHAR(255) NOT NULL,
    content_hash VARCHAR(255) NOT NULL,
    thumbnail_url VARCHAR(255) NOT NULL DEFAULT '',
    content_type VARCHAR(255) NOT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES documents(id),
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)

