"""initial schema

Revision ID: 1e02fb52ad1f
Revises: 
Create Date: 2026-06-01 02:43:00.007656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = '1e02fb52ad1f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', name='document_status'), nullable=False, server_default=sa.text("'pending'")),
    sa.Column('error', sa.Text(), nullable=True),
    sa.Column('content_url', sa.String(length=255), nullable=False),
    sa.Column('content_hash', sa.String(length=255), nullable=False),
    sa.Column('thumbnail_url', sa.String(length=255), nullable=False, server_default=sa.text("''")),
    sa.Column('content_type', sa.String(length=255), nullable=False),
    sa.Column('created_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.PrimaryKeyConstraint('id', name='pk_documents')
    )
    op.create_table('document_embeddings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('document_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('text_embedding', pgvector.sqlalchemy.vector.VECTOR(dim=384), nullable=True),
    sa.Column('image_embedding', pgvector.sqlalchemy.vector.VECTOR(dim=512), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_document_embeddings_document_id_documents'),
    sa.PrimaryKeyConstraint('id', name='pk_document_embeddings')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('document_embeddings')
    op.drop_table('documents')
    op.execute("DROP TYPE IF EXISTS document_status")
    op.execute("DROP EXTENSION IF EXISTS vector")
