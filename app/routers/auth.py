from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import UserModel
from app.schemas.user import UserResponse,UserRegister,TokenResponse,RefreshTokenResponse
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token
from app.core.config import settings
from jose import jwt,JWTError
router = APIRouter(prefix="/auth",tags=['Auth'])
@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(data:UserRegister,db:Session = Depends(get_db)):
    next_db = db.query(UserModel).filter(UserModel.email == data.email).first()
    if next_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email đã tồn tại")
    user = UserModel(
        email = data.email,
        password_hash = hash_password(data.password),
        full_name = data.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
@router.post("/login",response_model=TokenResponse)
def login(form_data:OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),db:Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password,user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Email hoặc mật khẩu ko chính xác")
    token = create_access_token({"sub":user.email,"role":user.role})
    refresh_token = create_refresh_token({"sub":user.email})
    return {
        "access_token":token,
        "refresh_token":refresh_token,
        "token_type":"bearer"}
@router.post("/refresh")
def refresh_token(body: RefreshTokenResponse, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token không hợp lệ")
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn")
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User không tồn tại hoặc đã bị khóa")
    new_access_token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": new_access_token, "token_type": "bearer"}