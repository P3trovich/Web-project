from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from tables.news import News
from tables.comments import Comment
from sqlalchemy import select
import schemas.comments as comment_schemas
from monitoring.monitoring import logger

class CommentService:

    async def create_comment(db: AsyncSession, comment: comment_schemas.CommentCreate, news_id: int, author_id: int):
        result = await db.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()
        if not news:
            logger.error(
                "failed_creating_comment",
                news_id=news_id,
                author_id=author_id
            )
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't create a comment"), {"status_code": "404"})
            raise HTTPException(status_code=404, detail="News not found")
        
        db_comment = Comment(**comment.model_dump(), news_id=news_id, author_id=author_id)
        db.add(db_comment)
        await db.commit()
        await db.refresh(db_comment)
        return db_comment

    async def get_comments(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(select(Comment).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_comments_by_news(db: AsyncSession, news_id: int):
        result = await db.execute(select(Comment).where(Comment.news_id == news_id))
        return result.scalars().all()

    async def update_comment(db: AsyncSession, comment_id: int, comment_update: comment_schemas.CommentCreate):
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        db_comment = result.scalar_one_or_none()
        if db_comment:
            for field, value in comment_update.model_dump().items():
                setattr(db_comment, field, value)
            await db.commit()
            await db.refresh(db_comment)
        return db_comment

    async def delete_comment(db: AsyncSession, comment_id: int):
        result = await db.execute(select(Comment).where(Comment.id == comment_id))
        db_comment = result.scalar_one_or_none()
        if db_comment:
            db.delete(db_comment)
            await db.commit()
        return db_comment