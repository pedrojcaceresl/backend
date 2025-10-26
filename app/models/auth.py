from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class UserRegister(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "STUDENT"  # Default role
    
    @validator('role')
    def validate_role(cls, v):
        """Convert English roles to Spanish"""
        role_mapping = {
            "ADMIN": "admin",
            "STUDENT": "estudiante", 
            "COMPANY": "empresa",
            "admin": "admin",
            "estudiante": "estudiante",
            "empresa": "empresa"
        }
        return role_mapping.get(v, "estudiante")  # Default to student

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