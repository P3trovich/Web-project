from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SessionInfo(BaseModel):
    user_id: int
    user_agent: Optional[str]
    created_at: str
    expires_at: str