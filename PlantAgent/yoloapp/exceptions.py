# -*- coding: utf-8 -*-
"""
异常处理模块

定义项目中所有自定义异常类，提供清晰的异常层次结构。
"""

from typing import Dict, Optional, Any


class AgentError(Exception):
    """Agent 基础异常类
    
    所有 Agent 相关异常的基类，提供统一的异常接口。
    
    Attributes:
        message: 错误消息
        error_code: 错误代码，用于程序化处理
        context: 错误上下文信息，包含额外的调试信息
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """初始化 Agent 异常
        
        Args:
            message: 错误消息描述
            error_code: 可选的错误代码
            context: 可选的上下文信息字典
        """
        self.message = message
        self.error_code = error_code or "AGENT_ERROR"
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """返回格式化的错误信息"""
        base_msg = f"[{self.error_code}] {self.message}"
        if self.context:
            base_msg += f" | Context: {self.context}"
        return base_msg
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于序列化"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context
        }


# ============================================================================
# 检测相关异常
# ============================================================================

class DetectionError(AgentError):
    """检测相关异常基类
    
    用于 YOLO 模型检测、图像处理等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "DETECTION_ERROR",
            context=context
        )


class ModelLoadError(DetectionError):
    """模型加载失败异常
    
    当 YOLO 模型无法加载时抛出。
    """
    
    def __init__(self, model_path: str, cause: Optional[Exception] = None):
        """初始化模型加载错误
        
        Args:
            model_path: 模型文件路径
            cause: 导致错误的原始异常
        """
        context = {
            "model_path": model_path,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"无法加载模型: {model_path}",
            error_code="MODEL_LOAD_FAILED",
            context=context
        )


class InferenceError(DetectionError):
    """模型推理失败异常
    
    当模型推理过程中发生错误时抛出。
    """
    
    def __init__(self, image_path: str, cause: Optional[Exception] = None):
        """初始化推理错误
        
        Args:
            image_path: 图像文件路径
            cause: 导致错误的原始异常
        """
        context = {
            "image_path": image_path,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"模型推理失败: {image_path}",
            error_code="INFERENCE_FAILED",
            context=context
        )


class ImageProcessError(DetectionError):
    """图像处理失败异常
    
    当图像预处理或后处理失败时抛出。
    """
    
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        """初始化图像处理错误
        
        Args:
            operation: 失败的操作名称
            cause: 导致错误的原始异常
        """
        context = {
            "operation": operation,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"图像处理失败: {operation}",
            error_code="IMAGE_PROCESS_FAILED",
            context=context
        )


# ============================================================================
# RAG 相关异常
# ============================================================================

class RAGError(AgentError):
    """RAG（检索增强生成）相关异常基类
    
    用于向量存储、嵌入、检索等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "RAG_ERROR",
            context=context
        )


class VectorStoreError(RAGError):
    """向量存储错误异常
    
    当向量数据库操作失败时抛出。
    """
    
    def __init__(self, operation: str, cause: Optional[Exception] = None):
        """初始化向量存储错误
        
        Args:
            operation: 失败的操作名称（如 'load', 'save', 'search'）
            cause: 导致错误的原始异常
        """
        context = {
            "operation": operation,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"向量存储操作失败: {operation}",
            error_code="VECTOR_STORE_FAILED",
            context=context
        )


class EmbeddingError(RAGError):
    """嵌入生成错误异常
    
    当文本嵌入生成失败时抛出。
    """
    
    def __init__(self, text_preview: str, cause: Optional[Exception] = None):
        """初始化嵌入错误
        
        Args:
            text_preview: 文本预览（前50个字符）
            cause: 导致错误的原始异常
        """
        context = {
            "text_preview": text_preview[:50],
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"嵌入生成失败: {text_preview[:30]}...",
            error_code="EMBEDDING_FAILED",
            context=context
        )


class RetrievalError(RAGError):
    """检索失败异常
    
    当知识库检索失败时抛出。
    """
    
    def __init__(self, query: str, cause: Optional[Exception] = None):
        """初始化检索错误
        
        Args:
            query: 查询文本
            cause: 导致错误的原始异常
        """
        context = {
            "query": query,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"知识库检索失败: {query}",
            error_code="RETRIEVAL_FAILED",
            context=context
        )


# ============================================================================
# LLM 相关异常
# ============================================================================

class LLMError(AgentError):
    """LLM（大语言模型）相关异常基类
    
    用于 API 调用、Token 限制等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "LLM_ERROR",
            context=context
        )


class TokenLimitExceeded(LLMError):
    """Token 限制超出异常
    
    当请求的 Token 数量超过限制时抛出。
    """
    
    def __init__(
        self,
        current_tokens: int,
        max_tokens: int,
        request_tokens: int
    ):
        """初始化 Token 限制错误
        
        Args:
            current_tokens: 当前已使用的 Token 数
            max_tokens: 最大允许的 Token 数
            request_tokens: 本次请求需要的 Token 数
        """
        context = {
            "current_tokens": current_tokens,
            "max_tokens": max_tokens,
            "request_tokens": request_tokens,
            "exceeded_by": (current_tokens + request_tokens) - max_tokens
        }
        super().__init__(
            message=f"Token 限制超出: 当前 {current_tokens}, 请求 {request_tokens}, 最大 {max_tokens}",
            error_code="TOKEN_LIMIT_EXCEEDED",
            context=context
        )


class APIError(LLMError):
    """API 调用错误异常
    
    当 LLM API 调用失败时抛出。
    """
    
    def __init__(
        self,
        api_name: str,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None
    ):
        """初始化 API 错误
        
        Args:
            api_name: API 名称
            status_code: HTTP 状态码
            cause: 导致错误的原始异常
        """
        context = {
            "api_name": api_name,
            "status_code": status_code,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"API 调用失败: {api_name} (状态码: {status_code})",
            error_code="API_CALL_FAILED",
            context=context
        )


class RateLimitError(LLMError):
    """速率限制错误异常
    
    当 API 调用超过速率限制时抛出。
    """
    
    def __init__(self, retry_after: Optional[int] = None):
        """初始化速率限制错误
        
        Args:
            retry_after: 建议的重试等待时间（秒）
        """
        context = {
            "retry_after": retry_after
        }
        message = "API 速率限制超出"
        if retry_after:
            message += f"，请在 {retry_after} 秒后重试"
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            context=context
        )


class ModelNotFoundError(LLMError):
    """模型未找到异常
    
    当请求的 LLM 模型不存在时抛出。
    """
    
    def __init__(self, model_name: str):
        """初始化模型未找到错误
        
        Args:
            model_name: 模型名称
        """
        context = {"model_name": model_name}
        super().__init__(
            message=f"模型未找到: {model_name}",
            error_code="MODEL_NOT_FOUND",
            context=context
        )


# ============================================================================
# 工具相关异常
# ============================================================================

class ToolError(AgentError):
    """工具相关异常基类
    
    用于工具执行、参数验证等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "TOOL_ERROR",
            context=context
        )


class ExecutionError(ToolError):
    """工具执行失败异常
    
    当工具执行过程中发生错误时抛出。
    """
    
    def __init__(
        self,
        tool_name: str,
        operation: str,
        cause: Optional[Exception] = None
    ):
        """初始化执行错误
        
        Args:
            tool_name: 工具名称
            operation: 失败的操作
            cause: 导致错误的原始异常
        """
        context = {
            "tool_name": tool_name,
            "operation": operation,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"工具执行失败: {tool_name}.{operation}",
            error_code="TOOL_EXECUTION_FAILED",
            context=context
        )


class ParameterError(ToolError):
    """参数错误异常
    
    当工具参数验证失败时抛出。
    """
    
    def __init__(
        self,
        tool_name: str,
        parameter_name: str,
        expected_type: str,
        actual_value: Any
    ):
        """初始化参数错误
        
        Args:
            tool_name: 工具名称
            parameter_name: 参数名称
            expected_type: 期望的类型
            actual_value: 实际的值
        """
        context = {
            "tool_name": tool_name,
            "parameter_name": parameter_name,
            "expected_type": expected_type,
            "actual_value": str(actual_value),
            "actual_type": type(actual_value).__name__
        }
        super().__init__(
            message=f"参数错误: {tool_name}.{parameter_name} 期望 {expected_type}",
            error_code="PARAMETER_ERROR",
            context=context
        )


# ============================================================================
# Flow 相关异常
# ============================================================================

class FlowError(AgentError):
    """Flow 相关异常基类
    
    用于流程编排、Agent 协调等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "FLOW_ERROR",
            context=context
        )


class AgentNotFoundError(FlowError):
    """Agent 未找到异常
    
    当请求的 Agent 不存在时抛出。
    """
    
    def __init__(self, agent_key: str, available_agents: list):
        """初始化 Agent 未找到错误
        
        Args:
            agent_key: 请求的 Agent 键名
            available_agents: 可用的 Agent 列表
        """
        context = {
            "agent_key": agent_key,
            "available_agents": available_agents
        }
        super().__init__(
            message=f"Agent 未找到: {agent_key}，可用: {available_agents}",
            error_code="AGENT_NOT_FOUND",
            context=context
        )


class FlowExecutionError(FlowError):
    """Flow 执行失败异常
    
    当 Flow 执行过程中发生错误时抛出。
    """
    
    def __init__(
        self,
        flow_name: str,
        step: str,
        cause: Optional[Exception] = None
    ):
        """初始化 Flow 执行错误
        
        Args:
            flow_name: Flow 名称
            step: 失败的步骤
            cause: 导致错误的原始异常
        """
        context = {
            "flow_name": flow_name,
            "step": step,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"Flow 执行失败: {flow_name} 在步骤 {step}",
            error_code="FLOW_EXECUTION_FAILED",
            context=context
        )


class AgentStateError(FlowError):
    """Agent 状态错误异常
    
    当 Agent 处于不正确的状态时抛出。
    """
    
    def __init__(
        self,
        agent_name: str,
        current_state: str,
        expected_state: str
    ):
        """初始化 Agent 状态错误
        
        Args:
            agent_name: Agent 名称
            current_state: 当前状态
            expected_state: 期望状态
        """
        context = {
            "agent_name": agent_name,
            "current_state": current_state,
            "expected_state": expected_state
        }
        super().__init__(
            message=f"Agent 状态错误: {agent_name} 当前 {current_state}，期望 {expected_state}",
            error_code="AGENT_STATE_ERROR",
            context=context
        )


# ============================================================================
# 配置相关异常
# ============================================================================

class ConfigError(AgentError):
    """配置相关异常基类
    
    用于配置加载、验证等相关错误。
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code or "CONFIG_ERROR",
            context=context
        )


class ConfigLoadError(ConfigError):
    """配置加载失败异常
    
    当配置文件加载失败时抛出。
    """
    
    def __init__(self, config_path: str, cause: Optional[Exception] = None):
        """初始化配置加载错误
        
        Args:
            config_path: 配置文件路径
            cause: 导致错误的原始异常
        """
        context = {
            "config_path": config_path,
            "cause": str(cause) if cause else None
        }
        super().__init__(
            message=f"配置加载失败: {config_path}",
            error_code="CONFIG_LOAD_FAILED",
            context=context
        )


class ConfigValidationError(ConfigError):
    """配置验证失败异常
    
    当配置验证失败时抛出。
    """
    
    def __init__(self, field_name: str, validation_error: str):
        """初始化配置验证错误
        
        Args:
            field_name: 字段名称
            validation_error: 验证错误信息
        """
        context = {
            "field_name": field_name,
            "validation_error": validation_error
        }
        super().__init__(
            message=f"配置验证失败: {field_name} - {validation_error}",
            error_code="CONFIG_VALIDATION_FAILED",
            context=context
        )
