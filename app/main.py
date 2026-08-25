from fastapi import FastAPI

from app.routers import health, users, auth
from app.routers import event

from app.schemas.exceptions import setup_exceptions_handler

from app.db.database import Base, engine
from app.models import even_task, event as event_model, user


Base.metadata.create_all(bind=engine)
app = FastAPI()
@app.get("/")
def test_run():
    return {"message": "test success"}


setup_exceptions_handler(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(health.router)
app.include_router(event.router)