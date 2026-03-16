# -*- coding: utf-8 -*-
"""
Agent 工厂模块 - OpenManus 风格 + LangGraph
直接创建和管理 Agent 实例，支持 LangGraph 工作流

注意：已移除旧版 skill_client，改用 LangChain Tools 系统
"""

from typing import Optional

import config
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)

# 全局单例
_llm = None
_rag_service = None


def _init_llm():
    """初始化 LLM - 使用 LLMClient"""
    global _llm

    if _llm is not None:
        return _llm

    try:
        logger.info("初始化 LLM...")

        # 使用 yoloapp 的 LLMClient
        from yoloapp.llm import get_llm_client

        _llm = get_llm_client("default")
        logger.info(f"[OK] LLM 初始化成功: LLMClient")

    except Exception as e:
        logger.error(f"LLM 初始化失败: {e}")
        _llm = None

    return _llm


async def _init_rag_service():
    """初始化 RAG 服务"""
    global _rag_service

    if _rag_service is not None:
        return _rag_service

    try:
        logger.info("初始化 RAG 服务...")
        from yoloapp.rag import RAGService

        _rag_service = RAGService()
        await _rag_service.init_async()

        if _rag_service._initialized:
            logger.info("[OK] RAG 服务初始化成功")
        else:
            logger.warning("RAG 服务初始化未完成")
            _rag_service = None

    except Exception as e:
        logger.error(f"RAG 服务初始化失败: {e}")
        _rag_service = None

    return _rag_service


async def process_agent_request(user_question: str, image_path: Optional[str] = None):
    """
    处理 Agent 请求 - 临时使用旧的 Orchestrator（等待 langgraph 安装）

    Args:
        user_question: 用户问题
        image_path: 可选的图片路径

    Returns:
        处理结果字典
    """
    try:
        # 确保 RAG 已初始化
        if not _rag_service:
            await _init_rag_service()

        # 确保 LLM 已初始化
        if not _llm:
            _init_llm()

        # 使用 LangGraph 编排工作流
        try:
            logger.info(f"使用 LangGraph 编排工作流...")
            from yoloapp.flow.langgraph_workflow import run_langgraph_workflow

            result = await run_langgraph_workflow(user_question, image_path)
            return result
        except Exception as e:
            logger.error(f"工作流处理失败: {e}")
            return {
                "success": False,
                "response": f"处理失败: {str(e)}",
                "error": str(e),
                "agent_mode": "error",
            }

    except Exception as e:
        logger.error(f"处理请求失败: {e}")
        import traceback

        logger.error(traceback.format_exc())

        return {
            "success": False,
            "error": str(e),
            "response": "系统处理失败，请稍后重试",
            "agent_mode": "error",
        }


def get_llm():
    """获取 LLM 实例"""
    return _init_llm()


async def get_rag_service():
    """获取 RAG 服务实例"""
    return await _init_rag_service()


def get_tools():
    """
    获取可用的 LangChain Tools
    用于 API 端点返回工具列表
    """
    try:
        from yoloapp.tool.langchain_tools import get_all_tools

        tools = get_all_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in tools
        ]
    except Exception as e:
        logger.warning(f"获取工具列表失败: {e}")
        return []
