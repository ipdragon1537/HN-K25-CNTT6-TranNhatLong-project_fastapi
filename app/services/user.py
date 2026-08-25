from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import UserModel
from app.schemas.auth import RegisterRequest


def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def create_user(db: Session, data: RegisterRequest) -> UserModel:
    user = UserModel(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="USER",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def search_users(db: Session, keyword: Optional[str] = None) -> list[UserModel]:
    query = db.query(UserModel)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(or_(UserModel.full_name.ilike(like), UserModel.email.ilike(like)))
    return query.order_by(UserModel.id).all()