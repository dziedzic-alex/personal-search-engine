from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.document import Document


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    content: Mapped[str | None] = mapped_column(Text)
    text_embedding: Mapped[list[float] | None] = mapped_column(Vector(768))
    image_embedding: Mapped[list[float] | None] = mapped_column(Vector(768))
    created_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=datetime.now
    )

    document: Mapped[Document] = relationship(
        "Document", back_populates="document_embeddings", passive_deletes=True
    )
