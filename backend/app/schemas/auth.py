from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.users import UserRole

class RegisterRequest(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: str
    role: UserRole
    district: str
    state: Optional[str] = "Maharashtra"

class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    role: str
    district: str

    class Config:
        from_attributes = True