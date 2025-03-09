from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .db import Base

class NotificationDB(Base):
    __tablename__ = "notifications"

    id = Column(UUID, primary_key=True, default=uuid4)
    type = Column(String(50))
    status = Column(String(50))
    recipient = Column(String(255))
    content = Column(Text)
    variables = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
