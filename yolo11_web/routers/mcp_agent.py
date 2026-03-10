# -*- coding: utf-8 -*-
"""
MCP智能助手API路由
完全基于MCP工具和统一智能体服务
"""

import os
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from routers.deps import get_db
from config.settings import settings
from yoloapp.utils.logger import get_logger
# OpenManus 风格 + LangGraph：直接使用 Agent，无需 Service 包装
from routers.agent_factory import (
    process_agent_request,
    get_tools,
    get_rag_service
)

router = APIRouter(prefix="/api/agent", tags=["智能助手"])
logger = get_logger(__name__)


def allowed_file(filename: str) -> bool:
    """校验上传文件格式"""
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in settings.ALLOWED_EXTENSIONS


@router.post("/chat")
async def chat_with_agent(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    """
    与智能助手对话（OpenManus 风格 - 直接使用 Agent）

    Args:
        message: 用户消息
        image: 可选的图片文件
        db: 数据库会话

    Returns:
        智能助手回复
    """
    try:
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="消息不能为空")

        image_path = None

        # 处理图片上传
        if image and image.filename:
            logger.info(f"收到图片文件: {image.filename}")

            if not allowed_file(image.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件格式，仅允许：{','.join(settings.ALLOWED_EXTENSIONS)}",
                )

            # 保存图片
            filename = os.path.basename(image.filename)
            os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
            image_path = os.path.join(settings.UPLOAD_FOLDER, filename)

            with open(image_path, "wb") as f:
                content = await image.read()
                f.write(content)

            logger.info(f"图片保存成功: {image_path}")

        # OpenManus 风格：直接调用 Agent
        result = await process_agent_request(
            user_question=message, 
            image_path=image_path
        )

        if result.get("success"):
            return {
                "code": 200,
                "msg": "对话成功",
                "data": {
                    "message": message,
                    "response": result.get("response"),
                    "thinking_process": result.get("thinking_process"),
                    "agent_mode": result.get("agent_mode"),
                    "tools_used": result.get("tools_used", []),
                    "image_path": image_path,
                    # 九节点架构：流传式步骤（每步可见）
                    "stream_steps": result.get("stream_steps", []),
                    "stream_report": result.get("stream_report", ""),
                    "node_trace": result.get("node_trace", []),
                },
            }
        else:
            return {
                "code": 500,
                "msg": "处理失败",
                "data": {
                    "error": result.get("error"),
                    "thinking_process": result.get("thinking_process"),
                    "response": result.get("response", "处理失败"),
                },
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"智能助手对话异常: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"对话失败：{str(e)}")


@router.post("/chat/stream")
async def chat_with_agent_stream(
    message: str = Form(...), image: Optional[UploadFile] = File(None)
):
    """
    与智能助手对话（流式输出 - OpenManus 风格）

    Args:
        message: 用户消息
        image: 可选的图片文件

    Returns:
        SSE流式响应
    """
    from fastapi.responses import StreamingResponse
    import json

    async def event_generator():
        try:
            if not message or not message.strip():
                yield f"data: {json.dumps({'error': '消息不能为空'}, ensure_ascii=False)}\n\n"
                return

            image_path = None

            # 处理图片上传
            if image and image.filename:
                if not allowed_file(image.filename):
                    yield f"data: {json.dumps({'error': '不支持的文件格式'}, ensure_ascii=False)}\n\n"
                    return

                filename = os.path.basename(image.filename)
                os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
                image_path = os.path.join(settings.UPLOAD_FOLDER, filename)

                with open(image_path, "wb") as f:
                    content = await image.read()
                    f.write(content)

                # 发送图片上传成功事件
                yield f"data: {json.dumps({'type': 'image_uploaded', 'path': image_path}, ensure_ascii=False)}\n\n"

            # 发送开始处理事件
            yield f"data: {json.dumps({'type': 'processing_start', 'message': '开始处理请求...'}, ensure_ascii=False)}\n\n"

            # OpenManus 风格：直接调用 Agent
            result = await process_agent_request(
                user_question=message, 
                image_path=image_path
            )

            # 发送思考过程（分块发送）
            if result.get("thinking_process"):
                thinking_lines = result["thinking_process"].split("\n")
                for line in thinking_lines:
                    if line.strip():
                        yield f"data: {json.dumps({'type': 'thinking', 'content': line}, ensure_ascii=False)}\n\n"
                        await asyncio.sleep(0.05)  # 模拟流式输出

            # 发送最终结果
            yield f"data: {json.dumps({'type': 'response', 'content': result.get('response', ''), 'success': result.get('success', False)}, ensure_ascii=False)}\n\n"

            # 发送完成事件
            yield f"data: {json.dumps({'type': 'done', 'agent_mode': result.get('agent_mode'), 'tools_used': result.get('tools_used', [])}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式对话异常: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/tools")
async def get_available_tools():
    """
    获取所有可用的LangChain Tools

    Returns:
        可用工具列表
    """
    try:
        tools = get_tools()

        return {
            "code": 200,
            "msg": "获取工具列表成功",
            "data": {
                "tools": tools,
                "total": len(tools),
            },
        }

    except Exception as e:
        logger.error(f"获取工具列表异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取工具列表失败：{str(e)}")


@router.get("/memory/history")
async def get_memory_history(limit: int = 5):
    """
    获取记忆历史

    Args:
        limit: 返回数量限制

    Returns:
        历史记录
    """
    try:
        # 使用 MemoryManager
        from yoloapp.tool.memory_tool import get_memory_manager
        memory_manager = get_memory_manager()
        history = memory_manager.get_task_notes(limit=limit)
        
        return {"code": 200, "msg": "获取历史成功", "data": {"history": history}}

    except Exception as e:
        logger.error(f"获取历史异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取历史失败：{str(e)}")


@router.post("/memory/search")
async def search_memory(query: str = Form(...), limit: int = Form(5)):
    """
    搜索记忆

    Args:
        query: 搜索关键词
        limit: 返回数量限制

    Returns:
        搜索结果
    """
    try:
        # 使用 MemoryTool 搜索
        from yoloapp.tool.memory_tool import MemoryTool
        memory_tool = MemoryTool()
        result = await memory_tool.execute(action="search", query=query, limit=limit)
        
        return {
            "code": 200,
            "msg": "搜索成功",
            "data": {"query": query, "results": result.output if result.success else []},
        }

    except Exception as e:
        logger.error(f"搜索记忆异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败：{str(e)}")


@router.get("/status")
async def get_agent_status():
    """
    获取智能体状态（OpenManus 风格）

    Returns:
        智能体状态信息
    """
    try:
        # 获取各个组件
        from routers.agent_factory import get_llm, get_rag_service
        
        llm = get_llm()
        rag_service = await get_rag_service()
        
        # 获取 LangChain Tools 数量
        tools = get_tools()
        tools_count = len(tools)

        return {
            "code": 200,
            "msg": "获取状态成功",
            "data": {
                "llm_initialized": llm is not None,
                "rag_initialized": rag_service is not None,
                "agent_mode": "nine_node_with_langchain_tools",
                "tools_count": tools_count,
                "architecture": "OpenManus Style - LangChain Tools",
            },
        }

    except Exception as e:
        logger.error(f"获取状态异常: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败：{str(e)}")
