from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    is_verified_author = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    avatar = Column(String(200), nullable=True)
    password = Column(String(255), nullable=True)
    github_id = Column(String, nullable=True)