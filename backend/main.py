from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from routers import users_router, news_router, comments_router, metrics_router
from auth.router import router as auth_router
from contextlib import asynccontextmanager
from redis_cache.redis_client import init_redis, close_redis

@asynccontextmanager
async def lifespan(app):
    print("Starting up...")
    try:
        await init_redis()
        print("Redis initialized successfully")
    except Exception as e:
        print(f"Failed to initialize Redis: {e}")
        raise
    
    yield
    
    print("Shutting down...")
    try:
        await close_redis()
        print("Redis connection closed")
    except Exception as e:
        print(f"Error while closing Redis: {e}")

app = FastAPI(title="News API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(news_router)
app.include_router(comments_router)
app.include_router(metrics_router)

@app.get("/")
def read_root():
    return {"message": "News API is running"}

# Глобальная переменная для hawk
hawk = None

# Функция для получения hawk (не для инициализации!)
def get_hawk():
    global hawk
    return hawk

# Функция инициализации (вызывается один раз)
def init_hawk():
    global hawk
    
    # Если уже инициализирован, возвращаем
    if hawk is not None:
        return hawk
    
    try:
        from hawk_python_sdk.modules.fastapi import HawkFastapi
        
        hawk = HawkFastapi({
            'app_instance': app,
            'token': os.getenv('HAWK_TOKEN')
        })
        print("Hawk initialized successfully")
        
    except Exception as e:
        print(f"Hawk initialization error: {e}")
    
    return hawk

# Инициализируем hawk ДО старта приложения
init_hawk()