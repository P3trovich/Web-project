import time
import random
import signal
import sys
from celery_.app import create_celery_app
from datetime import datetime
from celery_.logger import get_logger
from celery_.service import get_news_for_current_week_sync

logger = get_logger()

app = create_celery_app()

def calculate_backoff(retry_count: int) -> int:
    """Exponential backoff with jitter"""
    base_delay = 2
    max_delay = 60
    delay = min(base_delay * (2 ** retry_count), max_delay)
    jitter = random.uniform(0.1, 0.3) * delay
    return int(delay + jitter)

# Graceful shutdown обработчик
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Задача запускается при создании новости
@app.task(name='celery_.tasks.send_email_task', bind=True, max_retries=3)
def send_email_task(self, users_data: list, news_data: dict):
    try:
        if not self.request.called_directly:
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
        logger.info(f"\n\n")
        logger.info("=" * 80)
        logger.info(f"Начинаю рассылку {len(users_data)} пользователям")
        logger.info("=" * 80)
        logger.info(f"📰 Новость")
        logger.info("─" * 80)
        logger.info(f"Заголовок: {news_data['title']}")
        logger.info(f"ID автора: {news_data['author_id']}")
        logger.info(f"Дата публикации: {news_data['publication_date'].date().strftime('%d.%m.%Y')}")
        logger.info(f"Содержание: {news_data['content']}")
        logger.info("─" * 80)
        for user in users_data:
            logger.info(f"Отправляю рассылку пользовелю {user['name']}")
        
        if random.random() < 0.3:
            raise Exception("Симулирую ошибки отправки")
        
        time.sleep(2)
        logger.info(f"Рассылка успешна отправлена {len(users_data)} пользователям")
        
        return {"status": "success", "count": len(users_data)}
        
    except Exception as exc:
        retry_count = self.request.retries
        backoff_delay = calculate_backoff(retry_count)
        
        if retry_count < self.max_retries:
            logger.warning(f"Retry {retry_count + 1}/{self.max_retries} in {backoff_delay}s")
            raise self.retry(countdown=backoff_delay, exc=exc)
        else:
            logger.error(f"Failed after {retry_count + 1} attempts: {exc}")
            return {"status": "failed", "error": str(exc)}
        
# Задача которая запускается по воскресеньям и логирует новости за неделю 
@app.task(name='celery_.tasks.sunday_reminder_task')
def sunday_reminder_task():
    current_time = datetime.now()
    
    try:
        # Получаем новости за текущую неделю
        weekly_news, start_of_week, end_of_week = get_news_for_current_week_sync()
        
        # Логируем заголовок отчета
        logger.info(f"\n\n")
        logger.info("=" * 80)
        logger.info("📊 ЕЖЕНЕДЕЛЬНЫЙ ДАЙДЖЕСТ НОВОСТЕЙ")
        logger.info("=" * 80)
        logger.info(f"Период: {start_of_week.strftime('%d.%m.%Y')} - {end_of_week.strftime('%d.%m.%Y')}")
        logger.info(f"Дата формирования: {current_time.strftime('%d.%m.%Y %H:%M:%S')}")
        logger.info(f"Всего новостей за неделю: {len(weekly_news)}")
        logger.info("=" * 80)
        
        if not weekly_news:
            logger.info("ℹ️ За эту неделю новостей не было")
        else:
            # Логируем каждую новость
            for i, news in enumerate(weekly_news, 1):
                logger.info(f"📰 Новость #{i}")
                logger.info("─" * 80)
                logger.info(f"Заголовок: {news.title}")
                logger.info(f"Автор ID: {news.author_id}")
                logger.info(f"Дата публикации: {news.publication_date.strftime('%d.%m.%Y')}")
                logger.info(f"Содержание: {news.content}")
                logger.info("─" * 80)
        
        # Статистика в конце
        logger.info(f"📈 Статистика: {len(weekly_news)} новостей за неделю")
        logger.info("=" * 80)
        
        return {
            "status": "completed", 
            "message": "Weekly digest generated successfully",
            "period": f"{start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}",
            "news_count": len(weekly_news)
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка при формировании дайджеста: {str(e)}")
        
        return {
            "status": "failed", 
            "error": str(e),
            "timestamp": current_time.isoformat()
        }