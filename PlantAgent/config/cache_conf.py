# -*- coding: utf-8 -*-
"""
Redis缓存配置
"""

import redis.asyncio as aioredis
from typing import Optional
from config.settings import settings

# 全局Redis客户端
redis_client: Optional[aioredis.Redis] = None


async def init_redis():
    """初始化Redis连接"""
    global redis_client
    try:
        redis_client = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        await redis_client.ping()
        print("✅ Redis连接成功")
    except Exception as e:
        print(f"⚠️ Redis连接失败: {e}")
        redis_client = None


async def close_redis():
    """关闭Redis连接"""
    global redis_client
    if redis_client:
        await redis_client.close()
        print("✅ Redis连接已关闭")


async def get_redis() -> Optional[aioredis.Redis]:
    """获取Redis客户端"""
    return redis_client
