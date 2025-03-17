from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from pydantic import BaseModel, Field

class NotificationBase(BaseModel):
    type: str
    recipient: str
    content: str
    variables: Dict = Field(default_factory=dict)

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(NotificationBase):
    type: Optional[str] = None
    recipient: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[Dict] = None
    status: Optional[str] = None

class NotificationInDB(NotificationBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True