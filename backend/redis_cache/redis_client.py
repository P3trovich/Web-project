import redis.asyncio as redis
import os

redis_client = None

async def init_redis():
    global redis_client
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_client = redis.Redis(host=redis_host, port=6379, decode_responses=True)
    return redis_client

async def get_redis():
    return redis_client

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()