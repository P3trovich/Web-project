from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from base import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    publication_date = Column(DateTime(timezone=True), server_default=func.now())