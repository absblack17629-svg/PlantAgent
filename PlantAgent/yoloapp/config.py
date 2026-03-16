# -*- coding: utf-8 -*-
"""
配置管理模块

提供统一的配置访问接口。
"""

from typing import Optional
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class LLMConfig:
    """LLM 配置"""
    # 智谱/火山引擎配置
    zhipu_api_key: str
    zhipu_base_url: str
    zhipu_model: str
    
    # 阿里千问配置
    dashscope_api_key: str
    dashscope_base_url: str
    dashscope_model: str
    
    # 通用配置
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60


@dataclass
class YOLOConfig:
    """YOLO 模型配置"""
    model_path: str
    confidence_threshold: float = 0.5
    input_size: int = 640


@dataclass
class RAGConfig:
    """RAG 配置"""
    vector_store_path: str
    embedding_model: str
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    offline_mode: bool = True


class ConfigManager:
    """配置管理器
    
    统一管理所有配置，从 config.settings 读取。
    """
    
    def __init__(self):
        """初始化配置管理器"""
        from config.settings import settings
        
        # LLM 配置
        self.llm = LLMConfig(
            zhipu_api_key=settings.ZHIPU_API_KEY,
            zhipu_base_url=settings.ZHIPU_BASE_URL,
            zhipu_model=settings.ZHIPU_MODEL,
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
            dashscope_base_url=settings.DASHSCOPE_API_URL,
            dashscope_model=settings.DASHSCOPE_MODEL,
            max_tokens=2000,
            temperature=0.7,
            timeout=60
        )
        
        # YOLO 配置
        self.yolo = YOLOConfig(
            model_path=settings.MODEL_PATH,
            confidence_threshold=settings.MODEL_CONFIDENCE_THRESHOLD,
            input_size=settings.MODEL_INPUT_SIZE
        )
        
        # RAG 配置
        self.rag = RAGConfig(
            vector_store_path=settings.VECTOR_STORE_PATH,
            embedding_model=settings.EMBEDDING_MODEL,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            top_k=settings.TOP_K,
            offline_mode=settings.OFFLINE_MODE
        )


@lru_cache()
def get_config_manager() -> ConfigManager:
    """获取配置管理器单例
    
    Returns:
        ConfigManager 实例
    """
    return ConfigManager()
