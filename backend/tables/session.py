from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from base import Base

class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    refresh_token = Column(String(500), unique=True, index=True, nullable=False)
    user_agent = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())