from .users import router as users_router
from .news import router as news_router
from .comments import router as comments_router
from .metrics import router as metrics_router

__all__ = ["users_router", "news_router", "comments_router", "metrics_router"]