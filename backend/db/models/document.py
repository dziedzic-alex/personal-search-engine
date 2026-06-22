import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from db.models.document_embedding import DocumentEmbedding


class DocumentStatus(enum.StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


MAX_NUM_ATTEMPTS = 3


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(
            DocumentStatus,
            name="document_status",
            values_callable=lambda enum_members: [
                enum_member.value for enum_member in enum_members
            ],
        ),
        insert_default=DocumentStatus.PENDING,
    )
    num_attempts: Mapped[int] = mapped_column(Integer, insert_default=0)
    s3_content_key: Mapped[str] = mapped_column(String(255))
    s3_thumbnail_key: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[int] = mapped_column(Integer)
    source_created_time: Mapped[datetime | None] = mapped_column(DateTime)
    created_time: Mapped[datetime] = mapped_column(
        DateTime, insert_default=datetime.now
    )

    document_embeddings: Mapped[list[DocumentEmbedding]] = relationship(
        "DocumentEmbedding", back_populates="document", passive_deletes=True
    )
