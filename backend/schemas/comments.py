from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    publication_date: datetime
    news_id: int
    author_id: int
    
    class Config:
        from_attributes = True