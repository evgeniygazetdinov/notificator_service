from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .db import Base


class NotificationDB(Base):
    __tablename__ = "notifications"

    id = Column(UUID, primary_key=True, default=uuid4)
    type = Column(String(50))
    status = Column(String(50))
    recipient = Column(String(255))
    subject = Column(String(255))
    body = Column(Text)
    variables = Column(JSONB, default={})
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
