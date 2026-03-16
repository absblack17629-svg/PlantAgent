# -*- coding: utf-8 -*-
"""
配置模块
"""

from config.settings import settings, get_settings
from config.db_conf import get_db, init_db, Base
from config.cache_conf import get_redis, init_redis, close_redis

# 兼容旧代码的配置字典
LLM_CONFIG = {
    "provider": "zhipu",
    "model": settings.ZHIPU_MODEL,
    "api_key": settings.ZHIPU_API_KEY,
    "base_url": settings.ZHIPU_API_URL,
    "temperature": 0.3,
    "max_tokens": 4000  # 增加到 4000，给推理模型足够的空间
}

MYSQL_CONFIG = {
    "host": settings.MYSQL_HOST,
    "port": settings.MYSQL_PORT,
    "user": settings.MYSQL_USER,
    "password": settings.MYSQL_PASSWORD,
    "database": settings.MYSQL_DATABASE,
    "charset": "utf8mb4"
}

REDIS_CONFIG = {
    "host": settings.REDIS_HOST,
    "port": settings.REDIS_PORT,
    "password": settings.REDIS_PASSWORD,
    "db": settings.REDIS_DB
}

RAG_CONFIG = {
    "vector_store_path": settings.VECTOR_STORE_PATH,
    "embedding_model": settings.EMBEDDING_MODEL,
    "chunk_size": settings.CHUNK_SIZE,
    "chunk_overlap": settings.CHUNK_OVERLAP,
    "top_k": settings.TOP_K,
    "offline_mode": settings.OFFLINE_MODE,
    "local_cache_dir": "~/.cache/huggingface/hub"
}

__all__ = [
    "settings",
    "get_settings",
    "get_db",
    "init_db",
    "Base",
    "get_redis",
    "init_redis",
    "close_redis",
    "LLM_CONFIG",
    "MYSQL_CONFIG",
    "REDIS_CONFIG",
    "RAG_CONFIG"
]

