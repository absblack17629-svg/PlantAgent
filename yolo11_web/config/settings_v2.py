# -*- coding: utf-8 -*-
"""
改进的配置管理系统
按照 OpenManus 风格组织配置
"""

import os
from typing import Optional, Set
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class LLMSettings(BaseSettings):
    """LLM 配置"""
    
    # 智谱AI配置
    zhipu_api_key: str = Field(default="", alias="ZHIPU_API_KEY")
    zhipu_api_url: str = Field(
        default="https://open.bigmodel.cn/api/anthropic",
        alias="ZHIPU_API_URL"
    )
    zhipu_model: str = Field(default="glm-4.6v-flash", alias="ZHIPU_MODEL")
    
    # 阿里千问配置
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    dashscope_model: str = Field(default="qwen-plus", alias="DASHSCOPE_MODEL")
    dashscope_api_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="DASHSCOPE_API_URL"
    )
    
    # 通用配置
    max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")
    temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    timeout: int = Field(default=30, alias="LLM_TIMEOUT")
    max_retries: int = Field(default=3, alias="LLM_MAX_RETRIES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class YOLOSettings(BaseSettings):
    """YOLO 模型配置"""
    
    model_path: str = Field(default="yolo11n.pt", alias="MODEL_PATH")
    confidence_threshold: float = Field(
        default=0.5,
        alias="MODEL_CONFIDENCE_THRESHOLD",
        ge=0.0,
        le=1.0
    )
    input_size: int = Field(default=640, alias="MODEL_INPUT_SIZE")
    device: str = Field(default="cpu", alias="YOLO_DEVICE")
    
    @field_validator("confidence_threshold")
    @classmethod
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class RAGSettings(BaseSettings):
    """RAG 配置"""
    
    vector_store_path: str = Field(
        default="./vector_store",
        alias="VECTOR_STORE_PATH"
    )
    embedding_model: str = Field(
        default="./models/sentence-transformers-all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL"
    )
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE", gt=0)
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP", ge=0)
    top_k: int = Field(default=3, alias="TOP_K", gt=0)
    offline_mode: bool = Field(default=True, alias="OFFLINE_MODE")
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap(cls, v, info):
        chunk_size = info.data.get("chunk_size", 500)
        if v >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class RedisSettings(BaseSettings):
    """Redis 配置"""
    
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT", gt=0, lt=65536)
    password: Optional[str] = Field(default="123456", alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB", ge=0)
    max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    socket_timeout: int = Field(default=5, alias="REDIS_SOCKET_TIMEOUT")
    
    @property
    def url(self) -> str:
        """生成 Redis 连接 URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    
    host: str = Field(default="localhost", alias="MYSQL_HOST")
    port: int = Field(default=3306, alias="MYSQL_PORT", gt=0, lt=65536)
    user: str = Field(default="root", alias="MYSQL_USER")
    password: str = Field(default="123456", alias="MYSQL_PASSWORD")
    database: str = Field(default="yolo_detect", alias="MYSQL_DATABASE")
    charset: str = Field(default="utf8mb4", alias="MYSQL_CHARSET")
    pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    
    @property
    def url(self) -> str:
        """生成异步 MySQL 连接 URL"""
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"
    
    @property
    def sync_url(self) -> str:
        """生成同步 MySQL 连接 URL"""
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset={self.charset}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class FileSettings(BaseSettings):
    """文件上传配置"""
    
    upload_folder: str = Field(default="static/uploads", alias="UPLOAD_FOLDER")
    result_folder: str = Field(default="static/results", alias="RESULT_FOLDER")
    max_upload_size: int = Field(
        default=10485760,  # 10MB
        alias="MAX_UPLOAD_SIZE"
    )
    allowed_extensions: Set[str] = Field(
        default={'png', 'jpg', 'jpeg', 'bmp'},
        alias="ALLOWED_EXTENSIONS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class SecuritySettings(BaseSettings):
    """安全配置"""
    
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


class AppConfig(BaseSettings):
    """应用主配置"""
    
    # 应用基础配置
    app_name: str = Field(default="YOLO11智能体系统", alias="APP_NAME")
    app_version: str = Field(default="2.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT", gt=0, lt=65536)
    
    # 系统功能开关
    enable_sentiment_analysis: bool = Field(
        default=True,
        alias="ENABLE_SENTIMENT_ANALYSIS"
    )
    enable_tool_planning: bool = Field(
        default=True,
        alias="ENABLE_TOOL_PLANNING"
    )
    streaming_response: bool = Field(
        default=True,
        alias="STREAMING_RESPONSE"
    )
    
    # 对话配置
    max_conversation_history: int = Field(
        default=10,
        alias="MAX_CONVERSATION_HISTORY",
        gt=0
    )
    
    # 子配置
    llm: LLMSettings = Field(default_factory=LLMSettings)
    yolo: YOLOSettings = Field(default_factory=YOLOSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    file: FileSettings = Field(default_factory=FileSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


@lru_cache()
def get_config() -> AppConfig:
    """获取配置单例"""
    return AppConfig()


# 导出配置实例
config = get_config()
