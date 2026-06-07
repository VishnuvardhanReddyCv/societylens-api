from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserOut(UserBase):
    id: str
    role: UserRole
    complex_id: str
    unit_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class RegisterRequest(BaseModel):
    complex_name: str
    city: str
    address: str
    name: str
    email: EmailStr
    password: str


class JoinRequest(BaseModel):
    invite_code: str
    name: str
    unit_number: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
