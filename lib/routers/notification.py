from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from lib.crud import notification as notification_crud
from sqlalchemy.orm import Session

from lib.db import get_db
from lib.schemas import NotificationBase, NotificationUpdate
from lib.queue.producer import NotificationProducer

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.post("/send")
def send_notification(notification: NotificationBase, db: Session = Depends(get_db)):
    """отправка с хендлером обработки уведомления"""
    notification_data = notification_crud.create_notification(db, notification)
    producer = NotificationProducer()
    # try:
    producer.send_notification(notification_data.type, notification_data)
    return {"status": "queued", "notification_id": notification_data.id}
    # except Exception as e:
        # notification_crud.update_notification(db, notification_data.id, {"status": "failed"})
    #     raise HTTPException(status_code=500, detail=str(e))
    # finally:
    #     producer.close()
    


@router.post("/delete")
def delete_notification(notification_id: UUID, db: Session = Depends(get_db)):
    return notification_crud.delete_notification(db, notification_id)
@router.put("/update")
def update_notification(notification_id: UUID, notification: NotificationUpdate, db: Session = Depends(get_db)):
    return notification_crud.update_notification(db, notification_id, notification)
@router.get("/list")
def get_notification_by_offset(offset: int, limit: int, db: Session = Depends(get_db)):
    return notification_crud.get_notifications(db, offset, limit)



@router.get("/{id}/status/")
def status(id: int, db: Session = Depends(get_db)):
    return notification_crud.get_notification(db, id)



@router.get("/history/status")
def history():
    return {"status": "ok"}


