from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "STUDENT"  # Default role

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict

class PasswordUpdate(BaseModel):
    """Password update model"""
    current_password: str
    new_password: str