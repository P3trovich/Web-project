from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewsBase(BaseModel):
    title: str
    content: str
    cover_image: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    publication_date: datetime
    author_id: int
    
    class Config:
        from_attributes = True