from db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Vector
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    text_embedding: Mapped[Vector(384)] = mapped_column(nullable=True)
    image_embedding: Mapped[Vector(512)] = mapped_column(nullable=True)
    created_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)