
import uuid

from fastapi import APIRouter, Request, HTTPException, Depends
from lib.crud import notification
from sqlalchemy.orm import Session

from lib.db import get_db
from lib.schemas import NotificationBase, NotificationUpdate
import lib.crud.notification  as notification_crud


router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.post("/send")
def send_notification(notification: NotificationBase, db: Session = Depends(get_db)):
    return notification_crud.create_notification(db, notification)


@router.get("/{id}/status/")
def read_item(id: int):
    return {"item_id": id}


@router.get("/history/status")
def history():
    return {"status": "ok"}


