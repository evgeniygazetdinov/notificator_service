from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


@router.post("/send")
def create():
    return {
    "channel": "email|sms",
    "template_id": "string",
    "recipient": "string",
    "variables": {
        "key": "value"
    },
    "priority": "high|normal|low"
}


@router.get("/{id}/status/")
def retrive(id: int):
    return {"item_id": id}


@router.get("/history")
def list():
    return {"status": "ok"}
