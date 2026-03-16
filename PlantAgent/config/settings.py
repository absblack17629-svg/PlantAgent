# -*- coding: utf-8 -*-
"""
全局配置管理
统一读取环境变量和配置
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "YOLO11智能体系统"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "yolo_detect"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = "123456"
    REDIS_DB: int = 0

    # 智谱AI配置 (保留兼容)
    ZHIPU_API_KEY: str = ""
    ZHIPU_API_URL: str = "https://open.bigmodel.cn/api/anthropic"
    ZHIPU_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/"  # 新增：兼容火山引擎
    ZHIPU_MODEL: str = "glm-4.7"  # 火山引擎模型名称

    # 阿里千问配置 (主用)
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_MODEL: str = "qwen-plus"
    DASHSCOPE_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 农业病虫害列表（用于对话压缩时的实体识别）
    RICE_DISEASES: str = (
        "稻瘟病,纹枯病,白叶枯,褐飞虱,稻纵卷叶螟,稻曲病,胡麻斑病,细菌性条斑病"
    )
    RICE_PESTS: str = "二化螟,三化螟,稻苞虫,稻瘿蚊,稻象甲,稻赤斑黑沫蝉"
    CROP_TYPES: str = "水稻,小麦,玉米,大豆,棉花,油菜,花生,蔬菜"

    @property
    def rice_disease_list(self) -> list:
        return [d.strip() for d in self.RICE_DISEASES.split(",")]

    @property
    def rice_pest_list(self) -> list:
        return [p.strip() for p in self.RICE_PESTS.split(",")]

    @property
    def crop_type_list(self) -> list:
        return [c.strip() for c in self.CROP_TYPES.split(",")]

    @property
    def agricultural_entities(self) -> list:
        """所有农业实体（病害+虫害+作物）"""
        return self.rice_disease_list + self.rice_pest_list + self.crop_type_list

    @property
    def agricultural_entities_pattern(self) -> str:
        """生成正则表达式模式"""
        entities = self.agricultural_entities
        return "|".join(entities)

    # Excel导出配置
    export_temp_dir: str = "./temp/exports"
    export_max_records: int = 10000

    # 天气API配置
    weather_api_key: str = ""
    weather_api_provider: str = "qweather"  # qweather/openweathermap

    # Tavily 网络搜索配置
    TAVILY_API_KEY: str = ""

    # 监控配置
    monitoring_enabled: bool = True
    monitoring_interval: int = 60  # 秒
    alert_email_enabled: bool = False
    alert_email_to: str = ""

    # 文件上传配置
    UPLOAD_FOLDER: str = "static/uploads"
    RESULT_FOLDER: str = "static/results"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "bmp"}

    # YOLO模型配置
    MODEL_PATH: str = "yolo11n.pt"
    MODEL_CONFIDENCE_THRESHOLD: float = 0.5
    MODEL_INPUT_SIZE: int = 640

    # RAG配置
    VECTOR_STORE_PATH: str = "./vector_store"
    EMBEDDING_MODEL: str = "./bge-small-zh-v1.5"  # 使用中文优化模型
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3
    OFFLINE_MODE: bool = True

    # 系统配置
    ENABLE_SENTIMENT_ANALYSIS: bool = True  # 情感分析
    ENABLE_TOOL_PLANNING: bool = True  # 工具规划
    MAX_CONVERSATION_HISTORY: int = 10  # 最大对话历史
    STREAMING_RESPONSE: bool = True  # 流式响应

    # 数据库URL（自动生成）
    @property
    def DATABASE_URL(self) -> str:
        """生成异步MySQL连接URL"""
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

    @property
    def REDIS_URL(self) -> str:
        """生成Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # 允许额外字段


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
