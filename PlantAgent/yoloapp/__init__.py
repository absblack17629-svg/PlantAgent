# -*- coding: utf-8 -*-
"""
YOLOApp - 统一的应用模块

提供所有核心功能的统一导出。
使用延迟导入避免循环依赖。
"""

# 延迟导入函数
def get_llm_client(config_name: str = "default"):
    """获取 LLM 客户端"""
    from yoloapp.llm import get_llm_client as _get_llm_client
    return _get_llm_client(config_name)


def get_config_manager():
    """获取配置管理器"""
    from yoloapp.config import get_config_manager as _get_config_manager
    return _get_config_manager()


def get_rag_service():
    """获取 RAG 服务"""
    from yoloapp.rag import get_rag_service as _get_rag_service
    return _get_rag_service()


# 导出常用类（延迟导入）
__all__ = [
    "get_llm_client",
    "get_config_manager",
    "get_rag_service",
]


# 提供类的访问（通过属性）
def __getattr__(name):
    """延迟导入类"""
    
    # LLM 相关
    if name == "LLMClient":
        from yoloapp.llm import LLMClient
        return LLMClient
    elif name == "TokenCounter":
        from yoloapp.token_counter import TokenCounter
        return TokenCounter
    
    # 异常
    elif name in ["AgentError", "DetectionError", "RAGError", "LLMError", "APIError"]:
        from yoloapp.exceptions import (
            AgentError, DetectionError, RAGError, LLMError, APIError
        )
        return locals()[name]
    
    # RAG
    elif name == "RAGService":
        from yoloapp.rag import RAGService
        return RAGService
    
    # Schema
    elif name in ["Message", "Memory", "AgentState"]:
        from yoloapp.schema import Message, Memory, AgentState
        return locals()[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
