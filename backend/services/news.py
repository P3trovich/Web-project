from sqlalchemy.ext.asyncio import AsyncSession
from tables.news import News
from tables.comments import Comment
from fastapi import HTTPException
import schemas.news as news_schemas
from sqlalchemy import select, delete
from redis_cache.redis_client import get_redis
import json
from datetime import datetime
from services.users import UserService
from celery_.tasks import send_email_task
from monitoring.monitoring import logger

class NewsService:

    async def create_news(db: AsyncSession, news: news_schemas.NewsCreate, author_id: int):
        redis_client = await get_redis()
        cache_key = f"news_id:all"

        db_news = News(**news.model_dump(), author_id=author_id)
        try:
            users = await UserService.get_users(db=db)
            # Преобразуем SQLAlchemy объекты в словари
            users_data = []
            for user in users:
                users_data.append({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                })

            # Преобразуем новость в словарь

            news_data = {
                "id": db_news.id,
                "title": db_news.title,
                "content": db_news.content,
                "publication_date": datetime.now(),
                "author_id": db_news.author_id,
                "cover_image": db_news.cover_image
            }
            task = send_email_task.delay(users_data, news_data)
        except Exception as e:
            logger.error(
                "failed_creating_news",
                news_id=news.news_id,
                author_id=author_id
            )
            from main import get_hawk
            hawk = get_hawk()
            hawk.send(ValueError("Couldn't create news"), {"status_code": "500"})
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        db.add(db_news)
        await db.commit()
        await db.refresh(db_news)
    
        cached_news = await redis_client.get(cache_key)
    
        if cached_news:
            # Если кеш существует - обновляем его
            news_list_dict = json.loads(cached_news)
        
            news_dict = {
                "id": db_news.id,
                "title": db_news.title,
                "content": db_news.content,
                "publication_date": db_news.publication_date.isoformat() if db_news.publication_date else None,
                "author_id": db_news.author_id,
                "cover_image": db_news.cover_image
            }
            news_list_dict.append(news_dict)
        
            # Обновляем кеш
            expire_seconds = 300
            await redis_client.set(cache_key, json.dumps(news_list_dict), ex=expire_seconds)
            print("Кеш обновлен новой новостью")
        else:
            print("Кеш не существует, будет создан при следующем запросе")
    
        return db_news

    async def get_news(db: AsyncSession, skip: int = 0, limit: int = 100):
        redis_client = await get_redis()
        cache_key = f"news_id:all"
        # Проверяем кеш
        cached_news = await redis_client.get(cache_key)
        if cached_news:
            print("Все новости есть в кеше! Возвращаем...")
            # Возвращаем словарь python
            news_data = json.loads(cached_news)
            # Создаем объект News, превращая словарь в именованные аргументы
            return [News(**news_data) for news_data in news_data]
        
        print("Всех новостей нет в кеше( сейчас засунем...")
        result = await db.execute(
            select(News)
            .offset(skip)
            .limit(limit)
        )
        news_items = result.scalars().all()
        # Преобразуем все новости в список словарей
        news_list_dict = []
        for news_item in news_items:
            news_dict = {
                "id": news_item.id,
                "title": news_item.title,
                "content": news_item.content,
                "publication_date": news_item.publication_date.isoformat() if news_item.publication_date else None,
                "author_id": news_item.author_id,
                "cover_image": news_item.cover_image
            }
            news_list_dict.append(news_dict)
        # 300 секунд
        expire_seconds = 300
        await redis_client.set(cache_key, json.dumps(news_list_dict), ex=expire_seconds)
    
        return news_list_dict

    async def get_news_by_id(db: AsyncSession, news_id: int):
        redis_client = await get_redis()
        cache_key = f"news_id:{news_id}"
        # Проверяем кеш
        cached_news = await redis_client.get(cache_key)
        if cached_news:
            print("Новость есть в кеше! Возвращаем...")
            # Возвращаем словарь python
            news_data = json.loads(cached_news)
            # Создаем объект News, превращая словарь в именованные аргументы
            return News(**news_data)
        print("Новости нет в кеше( сейчас засунем...")
        result = await db.execute(select(News).where(News.id == news_id))
        news_item = result.scalar_one_or_none()
        if not news_item:
            return None
        news_dict = {
            "id": news_item.id,
            "title": news_item.title,
            "content": news_item.content,
            "publication_date": news_item.publication_date.isoformat() if news_item.publication_date else None,
            "author_id": news_item.author_id,
            "cover_image": news_item.cover_image
        }
        # 300 секунд
        expire_seconds = 300
        await redis_client.set(cache_key, json.dumps(news_dict), ex=expire_seconds)
    
        return news_item
    
    async def update_news(db: AsyncSession, news_id: int, news_update: news_schemas.NewsCreate):
        redis_client = await get_redis()
    
        # Получаем новость из БД
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalar_one_or_none()
    
        if not db_news:
            return None
    
        # Обновляем данные новости
        update_data = news_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_news, field, value)
    
        await db.commit()
        await db.refresh(db_news)
    
        # Подготавливаем данные для кэша
        news_dict = {
            "id": db_news.id,
            "title": db_news.title,
            "content": db_news.content,
            "publication_date": db_news.publication_date.isoformat() if db_news.publication_date else None,
            "author_id": db_news.author_id,
            "cover_image": db_news.cover_image
        }
    
        expire_seconds = 300

        # Обновляем кэш отдельной новости
        cache_key_single = f"news_id:{news_id}"
        await redis_client.set(cache_key_single, json.dumps(news_dict), ex=expire_seconds)
        print(f"Кэш отдельной новости {news_id} обновлен")

        # Обновляем кэш всех новостей
        cache_key_all = "news_id:all"
        cached_all_news = await redis_client.get(cache_key_all)

        if cached_all_news:
            news_list_dict = json.loads(cached_all_news)

            # Ищем и обновляем новость в списке всех новостей
            found = False
            for i, news_item in enumerate(news_list_dict):
                if news_item["id"] == news_id:
                    news_list_dict[i] = news_dict
                    found = True
                    break
        
            # Если не нашли, добавляем новую
            if not found:
                news_list_dict.append(news_dict)
        
            await redis_client.set(cache_key_all, json.dumps(news_list_dict), ex=expire_seconds)
            print("Кэш всех новостей обновлен")
        else:
            print("Кэш всех новостей не существует, будет создан при следующем запросе")
    
        return db_news

    async def delete_news_with_comments(db: AsyncSession, news_id: int):
        redis_client = await get_redis()
    
        result = await db.execute(select(News).where(News.id == news_id))
        db_news = result.scalar_one_or_none()
    
        if not db_news:
            return None
    
        # Удаляем комментарии
        await db.execute(delete(Comment).where(Comment.news_id == news_id))
        await db.delete(db_news)
        await db.commit()
    
        # Удаляем кэш отдельной новости
        cache_key_single = f"news_id:{news_id}"
        await redis_client.delete(cache_key_single)
        print(f"Кэш отдельной новости {news_id} удален")
    
        # Обновляем кэш всех новостей
        cache_key_all = "news_id:all"
        cached_all_news = await redis_client.get(cache_key_all)
    
        if cached_all_news:
            news_list_dict = json.loads(cached_all_news)
        
            # Удаляем новость из списка всех новостей
            news_list_dict = [news for news in news_list_dict if news["id"] != news_id]
        
            # Обновляем кэш всех новостей
            expire_seconds = 300
            await redis_client.set(cache_key_all, json.dumps(news_list_dict), ex=expire_seconds)
            print("Кэш всех новостей обновлен (удалена новость)")
        else:
            print("Кэш всех новостей не существует, ничего не делаем")
    
        return db_news