from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.service import AuthService
from tables.users import User
from tables.news import News
from tables.comments import Comment
from sqlalchemy import select
from redis_cache.redis_client import get_redis
import json
from monitoring.monitoring import logger

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
    ) -> User:
    token = credentials.credentials
    payload = AuthService.verify_token(token)

    if not payload:
        logger.error(
            "failed_getting_current_user",
            token=token
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload["type"] != "access":
        logger.error(
            "failed_putting_access_token",
            token=token
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required. Perhaps you pasted refresh token?"
        )
    
    user_id = payload["user_id"]
    redis_client = await get_redis()
    user_key = f"user_id:{user_id}"
    cached_user = await redis_client.get(user_key)
    if cached_user:
        print("Пользователь есть в кеше! Возвращаем...")
        # Возвращаем словарь python
        user_data = json.loads(cached_user)
        # Создаем объект News, превращая словарь в именованные аргументы
        return User(**user_data)
    print("Пользователя нет в кеше( сейчас засунем...")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.error(
            "failed_finding_user",
            user_id=user.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user_dict = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "registration_date": user.registration_date.isoformat(),
        "is_verified_author": user.is_verified_author,
        "is_admin": user.is_admin,
        "avatar": user.avatar,
        "password": user.password,
        "github_id": user.github_id
    }
    # 300 секунд
    expire_seconds = 300
    await redis_client.set(user_key, json.dumps(user_dict), ex=expire_seconds)
    
    return user

async def get_current_verified_author(
    current_user: User = Depends(get_current_user)
    ) -> User:
    if not current_user.is_verified_author and not current_user.is_admin:
        logger.error(
            "failed_verifying_author_priviliges",
            user_id=current_user.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified as author"
        )
    return current_user

def get_current_admin(
    current_user: User = Depends(get_current_user)
    ) -> User:
    if not current_user.is_admin:
        logger.error(
            "failed_verifying_admin_priviliges",
            user_id=current_user.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def verify_news_access(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalar_one_or_none()
    if not news:
        logger.error(
            "failed_getting_news",
            user_id=current_user.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    if news.author_id != current_user.id and not current_user.is_admin:
        logger.error(
            "failed_provinng_admin_or_author_priviliges",
            user_id=current_user.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this news"
        )

async def verify_comment_access(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to modify this comment"
        )