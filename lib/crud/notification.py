from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from lib.models import NotificationDB as Notification
from lib.queue.base import serialize_sqlalchemy
from lib.schemas import NotificationCreate, NotificationUpdate

def create_notification(db: Session, notification: NotificationCreate) -> Notification:
    db_notification = Notification(
        type=notification.type,
        status="pending",
        recipient=notification.recipient,
        content=notification.content,
        variables=notification.variables
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notification(db: Session, notification_id: UUID) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications(db: Session, skip: int = 0, limit: int = 100) -> List[Notification]:
    return db.query(Notification).offset(skip).limit(limit).all()

def update_notification(
    db: Session, 
    notification_id: UUID, 
    notification: NotificationUpdate
) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if db_notification:
        update_data = dict(notification)
        for key, value in update_data.items():
            setattr(db_notification, key, value)
        db.commit()
        db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: UUID) -> bool:
    notification = get_notification(db, notification_id)
    if notification:
        db.delete(notification)
        db.commit()
        return True
    return False