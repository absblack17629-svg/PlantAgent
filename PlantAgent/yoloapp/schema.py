# -*- coding: utf-8 -*-
"""
数据模型定义

合并所有 Schema 模型到单一文件。
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import json


# ============ Agent 相关 ============

class AgentRole(str, Enum):
    """Agent 角色枚举"""
    DETECTION = "detection"
    KNOWLEDGE = "knowledge"
    PLANNING = "planning"
    PLANNER = "planner"
    COORDINATOR = "coordinator"
    GENERAL = "general"
    INTENT_ANALYZER = "intent_analyzer"
    CONTEXT_MANAGER = "context_manager"
    MEMORY_MANAGER = "memory_manager"
    VALIDATOR = "validator"
    EXECUTOR = "executor"
    KNOWLEDGE_RETRIEVER = "knowledge_retriever"
    RESPONSE_GENERATOR = "response_generator"


class AgentState(str, Enum):
    """Agent 状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    PAUSED = "paused"


class AgentConfig(BaseModel):
    """Agent 配置模型"""
    name: str = Field(..., description="Agent 名称")
    role: AgentRole = Field(..., description="Agent 角色")
    description: Optional[str] = Field(None, description="Agent 描述")
    max_steps: int = Field(default=10, description="最大执行步骤数", ge=1, le=100)
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM 配置")
    tools: Optional[list] = Field(default_factory=list, description="可用工具列表")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    class Config:
        use_enum_values = True


# ============ Message 相关 ============

class ToolCall(BaseModel):
    """工具调用模型"""
    id: str = Field(..., description="工具调用 ID")
    type: str = Field(default="function", description="调用类型")
    function: Dict[str, Any] = Field(..., description="函数信息")


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色")
    content: Optional[str] = Field(None, description="消息内容")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="工具调用列表")
    tool_call_id: Optional[str] = Field(None, description="工具调用 ID")
    name: Optional[str] = Field(None, description="工具名称")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = {"role": self.role}
        
        if self.content is not None:
            data["content"] = self.content
        
        if self.tool_calls is not None:
            data["tool_calls"] = [tc.model_dump() for tc in self.tool_calls]
        
        if self.tool_call_id is not None:
            data["tool_call_id"] = self.tool_call_id
        
        if self.name is not None:
            data["name"] = self.name
        
        return data
    
    def to_llm_format(self) -> Dict[str, Any]:
        """转换为 LLM API 格式"""
        return self.to_dict()
    
    @classmethod
    def user_message(cls, content: str, **kwargs) -> "Message":
        return cls(role="user", content=content, **kwargs)
    
    @classmethod
    def system_message(cls, content: str, **kwargs) -> "Message":
        return cls(role="system", content=content, **kwargs)
    
    @classmethod
    def assistant_message(cls, content: Optional[str] = None, **kwargs) -> "Message":
        return cls(role="assistant", content=content, **kwargs)


class Memory(BaseModel):
    """记忆管理模型"""
    messages: List[Message] = Field(default_factory=list, description="消息列表")
    max_messages: int = Field(default=100, description="最大消息数量", ge=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent(self, n: int) -> List[Message]:
        return self.messages[-n:] if n > 0 else []
    
    def get_last_message(self) -> Optional[Message]:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None
    
    def get_last_user_message(self) -> Optional[Message]:
        """获取最后一条用户消息"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg
        return None
    
    def clear(self) -> None:
        self.messages.clear()


# ============ Tool 相关 ============

class ToolResult(BaseModel):
    """工具执行结果模型"""
    output: Any = Field(default=None, description="执行输出")
    error: Optional[str] = Field(default=None, description="错误信息")
    success: bool = Field(default=True, description="是否成功")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    
    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def success_result(cls, output: Any, **kwargs) -> "ToolResult":
        return cls(output=output, success=True, **kwargs)
    
    @classmethod
    def error_result(cls, error: str, **kwargs) -> "ToolResult":
        return cls(error=error, success=False, **kwargs)


class ToolParameter(BaseModel):
    """工具参数定义模型"""
    type: str = Field(default="object", description="参数类型")
    properties: Dict[str, Any] = Field(default_factory=dict, description="属性定义")
    required: list = Field(default_factory=list, description="必需参数")
    description: Optional[str] = Field(None, description="参数描述")


__all__ = [
    "AgentRole",
    "AgentState",
    "AgentConfig",
    "ToolCall",
    "Message",
    "Memory",
    "ToolResult",
    "ToolParameter",
]
