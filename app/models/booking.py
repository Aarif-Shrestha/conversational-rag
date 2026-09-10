from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    name = Column(String)
    email = Column(String)
    date = Column(String)
    time = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))