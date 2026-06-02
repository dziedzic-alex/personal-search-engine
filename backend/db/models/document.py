from db.base import Base
from sqlalchemy import String, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum
import enum
from db.models.document_embedding import DocumentEmbedding

class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus, 
            name="document_status",
            values_callable=lambda enum_members: [enum_member.value for enum_member in enum_members]),
            insert_default=DocumentStatus.PENDING)
    error: Mapped[str | None] = mapped_column(Text)
    content_url: Mapped[str] = mapped_column(String(255))
    content_hash: Mapped[str] = mapped_column(String(255))
    thumbnail_url: Mapped[str] = mapped_column(String(255), insert_default="")
    content_type: Mapped[str] = mapped_column(String(255))
    created_time: Mapped[datetime] = mapped_column(DateTime, insert_default=datetime.now)

    document_embeddings: Mapped[list["DocumentEmbedding"]] = relationship("DocumentEmbedding", back_populates="document")