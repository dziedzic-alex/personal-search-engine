from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    content: Mapped[str | None] = mapped_column(Text)
    text_embedding: Mapped[list[float] | None] = mapped_column(Vector(384))
    image_embedding: Mapped[list[float] | None] = mapped_column(Vector(512))
    created_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=datetime.now
    )

    document: Mapped[Document] = relationship(
        "Document", back_populates="document_embeddings"
    )
