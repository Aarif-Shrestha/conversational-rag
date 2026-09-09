from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    filename = Column(String)
    file_type = Column(String)
    chunking_strategy = Column(String)
    chunk_count = Column(Integer)
    uploaded_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )