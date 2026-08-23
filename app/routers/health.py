# check code
from app.db.database import get_db
from fastapi import APIRouter,Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
router= APIRouter(tags=['Health Check Code'])
@router.get("/health")
def heath_check_code(db:Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "Chạy đc"
    except Exception:
        db_status = "Lỗi"
    return {
        "status":"Online",
        "database":db_status,
        "message":"Chạy bình thường"
    }
