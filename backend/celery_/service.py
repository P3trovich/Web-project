import asyncio
import os
import sys
from datetime import datetime, timedelta
from celery_.logger import get_logger
from database import get_db

logger = get_logger()

def get_news_for_current_week_sync():
    """
    Синхронная функция для получения новостей за текущую неделю из БД.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # Поднимаемся на уровень выше celery_/
        sys.path.insert(0, project_root)
        from services.news import NewsService
        
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Создаем асинхронную функцию для работы с БД
        async def async_get_news():
            async for db in get_db():
                try:
                    all_news = await NewsService.get_news(db)
                    
                    # Фильтруем новости за текущую неделю
                    weekly_news = [
                        news for news in all_news
                        if start_of_week.date() <= news.publication_date.date() <= end_of_week.date()
                    ]
                    
                    logger.info(f"Found {len(weekly_news)} news for current week")
                    return weekly_news, start_of_week, end_of_week
                    
                except Exception as e:
                    logger.error(f"Error in async_get_news: {e}")
                    return [], start_of_week, end_of_week
        
        # Запускаем асинхронную функцию
        return asyncio.run(async_get_news())
        
    except Exception as e:
        logger.error(f"Error getting news from database: {e}")
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return [], start_of_week, end_of_week