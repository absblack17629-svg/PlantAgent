# -*- coding: utf-8 -*-
"""
LangGraph API 路由
提供与 LangGraph agent-chat-ui 兼容的 API 接口
"""

import uuid
import asyncio
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from yoloapp.utils.logger import get_logger

router = APIRouter(prefix="/api/threads", tags=["LangGraph API"])
logger = get_logger(__name__)

# OpenManus 风格：直接使用 Agent，无需 Service 包装
from routers.agent_factory import process_agent_request


# 数据模型
class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ThreadState(BaseModel):
    """线程状态模型"""
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateThreadRequest(BaseModel):
    """创建线程请求"""
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AddMessageRequest(BaseModel):
    """添加消息请求"""
    messages: List[Message]


class StreamConfig(BaseModel):
    """流配置"""
    stream_mode: str = "messages"


# 内存存储（生产环境应使用数据库）
threads_storage: Dict[str, ThreadState] = {}


@router.post("")
async def create_thread(request: CreateThreadRequest):
    """
    创建新的对话线程
    
    Returns:
        线程ID和初始状态
    """
    try:
        thread_id = str(uuid.uuid4())
        thread_state = ThreadState(metadata=request.metadata or {})
        threads_storage[thread_id] = thread_state
        
        logger.info(f"创建新线程: {thread_id}")
        
        return {
            "thread_id": thread_id,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": thread_state.metadata
        }
    
    except Exception as e:
        logger.error(f"创建线程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """
    获取线程状态
    
    Args:
        thread_id: 线程ID
    
    Returns:
        线程状态
    """
    try:
        if thread_id not in threads_storage:
            raise HTTPException(status_code=404, detail="线程不存在")
        
        thread_state = threads_storage[thread_id]
        
        return {
            "values": {
                "messages": [msg.dict() for msg in thread_state.messages]
            },
            "metadata": thread_state.metadata
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取线程状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/runs/stream")
async def stream_run(
    thread_id: str,
    request: Request
):
    """
    流式运行智能体 - 兼容 LangGraph 格式
    
    Args:
        thread_id: 线程ID
        request: 请求对象
    
    Returns:
        SSE流式响应
    """
    
    logger.info(f"=== 收到流式请求 - 线程: {thread_id} ===")
    
    async def event_generator():
        try:
            logger.info("开始生成事件流...")
            
            # 解析请求体
            body = await request.json()
            input_data = body.get("input", {})
            messages = input_data.get("messages", [])
            
            logger.info(f"收到流式请求 - 线程: {thread_id}, 消息数: {len(messages)}")
            
            if not messages:
                error_data = {"type": "error", "error": "消息不能为空"}
                yield f"event: error\ndata: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                return
            
            # 获取或创建线程
            if thread_id not in threads_storage:
                threads_storage[thread_id] = ThreadState()
                logger.info(f"创建新线程状态: {thread_id}")
            
            thread_state = threads_storage[thread_id]
            
            # 添加用户消息到线程
            for msg in messages:
                message = Message(**msg) if isinstance(msg, dict) else msg
                thread_state.messages.append(message)
                logger.info(f"添加消息: {message.role} - {message.content[:50]}...")
            
            # 获取最后一条用户消息和图片
            last_user_message = None
            image_path = None
            for msg in reversed(thread_state.messages):
                if msg.role == "user":
                    # 处理多种消息内容格式
                    if isinstance(msg.content, str):
                        last_user_message = msg.content
                    elif isinstance(msg.content, list):
                        # 可能是内容块列表 [text, image_url, ...]
                        text_parts = []
                        for block in msg.content:
                            if isinstance(block, dict):
                                if block.get("type") == "text":
                                    text_parts.append(block.get("text", ""))
                                elif block.get("type") == "image_url":
                                    # 提取图片URL/路径
                                    image_url = block.get("image_url", {})
                                    if isinstance(image_url, dict):
                                        url = image_url.get("url", "")
                                    elif isinstance(image_url, str):
                                        url = image_url
                                    else:
                                        url = ""
                                    
                                    # 如果是base64或http URL，记录下来
                                    if url.startswith("data:"):
                                        # Base64图片 - 暂时不支持，需要先保存
                                        logger.warning(f"收到base64图片，暂时不支持: {url[:50]}...")
                                    elif url.startswith("http"):
                                        image_path = url
                                    else:
                                        # 本地路径
                                        image_path = url
                            elif isinstance(block, str):
                                text_parts.append(block)
                        last_user_message = " ".join(text_parts)
                    break
            
            if not last_user_message:
                error_data = {"type": "error", "error": "未找到用户消息"}
                yield f"event: error\ndata: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                return
            
            logger.info(f"处理用户消息: {last_user_message[:50]}...")
            
            # 发送开始事件
            run_id = str(uuid.uuid4())
            metadata = {
                "run_id": run_id,
                "thread_id": thread_id,
                "langgraph_node": "agent"
            }
            yield f"event: metadata\ndata: {json.dumps(metadata, ensure_ascii=False)}\n\n"
            logger.info(f"发送 metadata 事件: {run_id}")
            
            # 发送处理中状态
            yield f"event: updates\ndata: {json.dumps({'type': 'processing'}, ensure_ascii=False)}\n\n"
            logger.info("发送 processing 状态")
            
            try:
                logger.info(f"调用 Agent 处理请求... image_path={image_path}")
                
                # OpenManus 风格：直接调用 Agent
                try:
                    result = await asyncio.wait_for(
                        process_agent_request(
                            user_question=last_user_message,
                            image_path=image_path
                        ),
                        timeout=60.0  # 60秒超时
                    )
                except asyncio.TimeoutError:
                    logger.error("Agent 处理超时")
                    result = {
                        "success": False,
                        "response": "处理超时，请稍后重试",
                        "error": "timeout",
                        "agent_mode": "nine_node"
                    }
                
                logger.info(f"Agent 处理完成，成功: {result.get('success')}")
                
                # 创建助手消息
                response_content = result.get("response", "抱歉，我无法处理您的请求。")
                assistant_message = Message(
                    role="assistant",
                    content=response_content
                )
                
                # 添加到线程
                thread_state.messages.append(assistant_message)
                logger.info(f"创建助手消息，长度: {len(response_content)}")
                
                # 发送完整消息（LangGraph 格式）
                message_data = {
                    "messages": [assistant_message.dict()]
                }
                yield f"event: updates\ndata: {json.dumps(message_data, ensure_ascii=False)}\n\n"
                logger.info("发送 updates 事件（消息）")
                
                # 发送完成事件
                end_data = {
                    "run_id": run_id
                }
                yield f"event: end\ndata: {json.dumps(end_data, ensure_ascii=False)}\n\n"
                logger.info(f"发送 end 事件")
                
                logger.info(f"流式响应完成 - 线程: {thread_id}")
                
            except Exception as e:
                logger.error(f"Agent 处理失败: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                
                # 发送错误但仍返回一个友好的消息
                assistant_message = Message(
                    role="assistant",
                    content=f"抱歉，处理您的请求时遇到了问题：{str(e)}"
                )
                thread_state.messages.append(assistant_message)
                
                message_data = {
                    "messages": [assistant_message.dict()]
                }
                yield f"event: updates\ndata: {json.dumps(message_data, ensure_ascii=False)}\n\n"
                
                end_data = {"run_id": run_id}
                yield f"event: end\ndata: {json.dumps(end_data, ensure_ascii=False)}\n\n"
        
        except Exception as e:
            logger.error(f"流式运行失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            error_data = {"type": "error", "error": str(e)}
            yield f"event: error\ndata: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    logger.info("返回 StreamingResponse")
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )


@router.get("/{thread_id}/history")
async def get_thread_history(thread_id: str, limit: int = 10):
    """
    获取线程历史消息
    
    Args:
        thread_id: 线程ID
        limit: 返回消息数量限制
    
    Returns:
        历史消息列表
    """
    try:
        if thread_id not in threads_storage:
            raise HTTPException(status_code=404, detail="线程不存在")
        
        thread_state = threads_storage[thread_id]
        messages = thread_state.messages[-limit:] if limit > 0 else thread_state.messages
        
        return {
            "messages": [msg.dict() for msg in messages],
            "total": len(thread_state.messages)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str):
    """
    删除线程
    
    Args:
        thread_id: 线程ID
    
    Returns:
        删除结果
    """
    try:
        if thread_id not in threads_storage:
            raise HTTPException(status_code=404, detail="线程不存在")
        
        del threads_storage[thread_id]
        logger.info(f"删除线程: {thread_id}")
        
        return {
            "success": True,
            "message": "线程已删除"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除线程失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assistants")
async def list_assistants():
    """
    列出可用的助手
    
    Returns:
        助手列表
    """
    return {
        "assistants": [
            {
                "assistant_id": "agent",
                "name": "YOLO11 智能助手",
                "description": "基于 YOLO11 的智能检测和对话助手",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }


@router.get("/info")
async def get_info():
    """
    获取 LangGraph 服务器信息（用于前端连接检查）
    
    Returns:
        服务器信息
    """
    return {
        "version": "1.0.0",
        "status": "ok",
        "server": "YOLO11 LangGraph API",
        "assistants": ["agent"]
    }
