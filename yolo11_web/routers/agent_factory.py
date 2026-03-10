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
_langgraph_app = None
_llm = None
_rag_service = None
_initialized = False


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


async def get_langgraph_app():
    """
    获取 LangGraph 工作流应用（单例模式）
    
    Returns:
        LangGraph 编译后的应用
    """
    global _langgraph_app, _initialized
    
    if _langgraph_app is not None and _initialized:
        return _langgraph_app
    
    logger.info("=" * 60)
    logger.info("初始化 LangGraph 九节点工作流")
    logger.info("=" * 60)
    
    try:
        # 1. 初始化 LLM
        llm = _init_llm()
        if llm is None:
            raise Exception("LLM 初始化失败")
        
        # 2. 初始化 RAG 服务（异步）
        rag_service = await _init_rag_service()
        
        # 3. 创建 LangGraph 工作流（使用 LangChain Tools）
        logger.info("创建 LangGraph 工作流...")
        from yoloapp.flow.nine_node_graph import create_nine_node_graph
        _langgraph_app = create_nine_node_graph()
        
        _initialized = True
        logger.info("[OK] LangGraph 工作流初始化完成")
        logger.info("=" * 60)
        
        return _langgraph_app
        
    except Exception as e:
        logger.error(f"[FAIL] LangGraph 工作流初始化失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


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
        
        # 尝试使用新的九节点工作流
        try:
            logger.info(f"尝试使用九节点 LangGraph 工作流...")
            from yoloapp.flow.nine_node_with_tools import run_nine_node_workflow
            result = await run_nine_node_workflow(user_question, image_path)
            return result
        except ImportError as e:
            logger.warning(f"LangGraph 未安装，回退到旧的 Orchestrator: {e}")
            logger.warning("请运行: install_langgraph_dependencies.bat")
            
            # 回退到旧的 Orchestrator
            from yoloapp.agent import create_nine_node_orchestrator
            from yoloapp.schema import Memory, Message
            
            orchestrator = create_nine_node_orchestrator()
            memory = Memory()
            memory.add_message(Message.user_message(user_question))
            memory.metadata["image_path"] = image_path
            orchestrator.memory = memory
            
            # 运行 orchestrator
            await orchestrator.run()
            
            # 获取最后一条助手消息
            response = ""
            for msg in reversed(memory.messages):
                if msg.role == "assistant":
                    response = msg.content
                    break
            
            return {
                "success": True,
                "response": response or "处理完成",
                "agent_mode": "nine_node_orchestrator_legacy",
                "warning": "使用旧版 Orchestrator，建议安装 LangGraph"
            }
        
    except Exception as e:
        logger.error(f"处理请求失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": str(e),
            "response": "系统处理失败，请稍后重试",
            "agent_mode": "error"
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
