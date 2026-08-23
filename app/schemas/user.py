from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict,Field
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Mật khẩu ít nhất 8 ký tự")
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenResponse(BaseModel):
    refresh_token: str