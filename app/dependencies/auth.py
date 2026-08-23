from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import get_db
from app.models.user import UserModel
oauth2_schemas = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(token:str = Depends(oauth2_schemas),db:Session = Depends(get_db)) -> UserModel:
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
        email:str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token ko hợp lệ hoặc đã hết hạn")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token ko hợp lệ hoặc đã hết hạn")
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token ko hợp lệ hoặc đã hết hạn")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Tài khoản đã bị khoá")
    return user
def require_admin(current_user:UserModel = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Ko có quyền admin")
    return current_user
 
        