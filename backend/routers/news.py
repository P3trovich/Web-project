from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.news import NewsService
import schemas.news as news_schemas
from services.comments import CommentService
import schemas.comments as comment_schemas
from auth.dependencies import get_current_verified_author, get_current_user, verify_news_access
from monitoring.monitoring import track_news_creation, logger

router = APIRouter(prefix="/news", tags=["news"])

@router.post("/", response_model=news_schemas.News)
@track_news_creation
async def create_news(
    news: news_schemas.NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_verified_author)
    ):
    logger.info(
            "creating_news",
            email=current_user.email
    )
    return await NewsService.create_news(db=db, news=news, author_id=current_user.id)

@router.get("/{news_id}/comments/", response_model=list[comment_schemas.Comment])
async def read_comments_by_news(
    news_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "getting_comments",
            news_id=news_id
    )
    return await CommentService.get_comments_by_news(db=db, news_id=news_id)

@router.get("/", response_model=list[news_schemas.News])
async def read_news(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "getting_news"
    )
    return await NewsService.get_news(db=db, skip=skip, limit=limit)

@router.get("/{news_id}", response_model=news_schemas.News)
async def read_news_by_id(
    news_id: int, 
    db: AsyncSession = Depends(get_db)
    ):
    logger.info(
            "getting_news_by_news_id",
            news_id=news_id
    )
    news = await NewsService.get_news_by_id(db=db, news_id=news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news

@router.put("/{news_id}", response_model=news_schemas.News)
async def update_news(
    news_id: int,
    news_update: news_schemas.NewsCreate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(verify_news_access)
):
    logger.info(
            "changing news",
            news_id=news_id
    )
    updated_news = await NewsService.update_news(db=db, news_id=news_id, news_update=news_update)
    return updated_news

@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(verify_news_access)
):
    logger.info(
            "deleting_news",
            news_id=news_id
    )
    deleted_news = await NewsService.delete_news_with_comments(db=db, news_id=news_id)
    return {"message": f"News with ID {news_id} and all comments deleted successfully"}

@router.post("/{news_id}/comments/", response_model=comment_schemas.Comment)
async def create_comment(
    news_id: int,
    comment: comment_schemas.CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(
            "creating_comment",
            news_id=news_id
    )
    return await CommentService.create_comment(
        db=db, 
        comment=comment, 
        news_id=news_id, 
        author_id=current_user.id
    )