from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import structlog
from pathlib import Path

# ===== Настройка structlog =====
def setup_monitoring():
    """Настройка логирования и метрик"""
    # Создаем директорию для логов
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка structlog
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(
            file=open(log_dir / "app.json.log", "a")
        )
    )
    
    return structlog.get_logger()

logger = setup_monitoring()

# ===== Prometheus метрики =====
NEWS_CREATED = Counter('news_created_total', 'Total news created')
USERS_REGISTERED = Counter('users_registered_total', 'Total users registered')
NOTIFICATIONS_SENT = Counter('notifications_sent_total', 'Total notifications sent')

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', 
                       ['method', 'endpoint', 'status_code'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# ===== Middleware для логирования запросов =====
class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path
        
        # Пропускаем эндпоинты мониторинга
        if path in ['/metrics', '/health']:
            return await call_next(request)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Обновляем метрики
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=path,
                status_code=response.status_code
            ).inc()
            
            REQUEST_LATENCY.observe(duration)
            
            # Логируем запрос в JSON
            logger.info(
                "http_request",
                method=request.method,
                path=path,
                status_code=response.status_code,
                duration=duration,
                client_ip=request.client.host if request.client else None
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Логируем ошибку
            logger.error(
                "http_error",
                method=request.method,
                path=path,
                error=str(e),
                error_type=type(e).__name__,
                duration=duration
            )
            
            raise

from functools import wraps

# ===== Декораторы для бизнес-метрик =====
def track_news_creation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        NEWS_CREATED.inc()
        
        logger.info(
            "news_created",
            news_id=getattr(result, 'id', None),
            user_id=kwargs.get('user_id', 'anonymous')
        )
        
        return result
    return wrapper

def track_user_registration(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        USERS_REGISTERED.inc()
        
        return result
    return wrapper

def track_notification(notification_type: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            from backend.monitoring.monitoring import NOTIFICATIONS_SENT
            from datetime import datetime
            
            try:
                result = func(*args, **kwargs)
                NOTIFICATIONS_SENT.inc()
                status = "success"
            except Exception as e:
                status = "error"
                # Логируем ошибку
                logger.error(
                    "notification_failed",
                    extra={
                        "notification_type": notification_type,
                        "status": status,
                        "error": str(e),
                        "event": "notification_sent",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
                raise
            else:
                # Логируем успех
                logger.info(
                    "notification_sent",
                    extra={
                        "notification_type": notification_type,
                        "status": status,
                        "event": "notification_sent",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            return result
        return wrapper
    return decorator