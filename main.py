from fastapi import FastAPI


from settings import settings, Base, engine

app = FastAPI(title=settings.PROJECT_NAME)
Base.metadata.create_all(bind=engine)

from lib.routers.notification import router as notification_router
from lib.routers.template import router as templates_router

app.include_router(notification_router)
app.include_router(templates_router)




@app.get("/api/v1/notifications/history")
def history():
    return {"Hello": "World"}