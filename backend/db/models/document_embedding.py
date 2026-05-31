from db.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Vector
from datetime import datetime


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=True)
    text_embedding = Column(Vector(384), nullable=True)
    image_embedding = Column(Vector(512), nullable=True)
    created_time = Column(DateTime, nullable=False, default=datetime.now)