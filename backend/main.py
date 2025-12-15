from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import users_router, news_router, comments_router, metrics_router
from auth.router import router as auth_router
from redis_cache.redis_client import init_redis, close_redis
from fastapi.middleware.cors import CORSMiddleware
from hawk_python_sdk.modules.fastapi import HawkFastapi
import os

app = FastAPI(title="News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hawk = HawkFastapi({
    'app_instance': app,
    'token': os.getenv('HAWK_TOKEN')
})

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
    hawk.send(ValueError("error description"), {"params": "value"})
    return {"message": "News API is running"}