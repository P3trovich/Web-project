from routers import users_router, news_router, comments_router, metrics_router
from auth.router import router as auth_router
from redis_cache.redis_client import init_redis, close_redis
from app_initialize_hawk import app

@app.on_event("startup")
async def startup_event():
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(news_router)
app.include_router(comments_router)
app.include_router(metrics_router)

@app.get("/")
def read_root():
    return {"message": "News API is running"}