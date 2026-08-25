from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.user import UserResponse
from app.dependencies.auth import get_current_user,require_admin
router = APIRouter(prefix="/users",tags=["User"])

@router.get("/me",response_model=UserResponse)
def get_me(current_user:UserModel = Depends(get_current_user)):
    return current_user

@router.get("",response_model=list[UserResponse])
def get_all_user(search:str | None = None,is_active:bool | None = None,admin:UserModel = Depends(require_admin),db:Session = Depends(get_db)):
    list_user = db.query(UserModel)
    if search:
        list_user = list_user.filter(or_(UserModel.full_name.ilike(f"%{search}%"),UserModel.email.ilike(f"%{search}%")))
    if is_active is not None:
        list_user = list_user.filter(UserModel.is_active == is_active)
    return list_user.filter(UserModel.role == "USER").all() 