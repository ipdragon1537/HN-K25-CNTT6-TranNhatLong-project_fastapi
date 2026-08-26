from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.db.database import Base, engine
from app.models import event,user,even_task
from app.routers import auth, event as event_router, event_task as event_task_router, users
from app.schemas.exceptions import setup_exceptions_handler
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Event Management API")

setup_exceptions_handler(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(event_router.router)
app.include_router(event_task_router.router)