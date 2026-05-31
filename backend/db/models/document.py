from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from datetime import datetime

class DocumentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), nullable=False)
    error = Column(Text, nullable=True)
    content_url = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False, default="")
    content_type = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False, default=datetime.now)