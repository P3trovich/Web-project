from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    registration_date: datetime
    is_verified_author: bool
    is_admin: bool
    
    class Config:
        from_attributes = True