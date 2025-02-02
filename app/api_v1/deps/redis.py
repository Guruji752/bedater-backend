# import aioredis
from typing import Optional
from app.settings.config import settings
from aioredis import Redis, from_url


# Redis connection setup
async def get_redis_connection():
	conn_str = settings.REDIS_HOST
	return await from_url(settings.REDIS_HOST, decode_responses=True)



  