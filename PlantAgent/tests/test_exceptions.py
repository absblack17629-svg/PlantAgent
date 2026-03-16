# -*- coding: utf-8 -*-
"""
异常模块测试

测试所有自定义异常类的功能和行为。
"""

import pytest
from services.exceptions import (
    AgentError,
    DetectionError,
    ModelLoadError,
    InferenceError,
    ImageProcessError,
    RAGError,
    VectorStoreError,
    EmbeddingError,
    RetrievalError,
    LLMError,
    TokenLimitExceeded,
    APIError,
    RateLimitError,
    ModelNotFoundError,
    ToolError,
    ExecutionError,
    ParameterError,
    FlowError,
    AgentNotFoundError,
    FlowExecutionError,
    AgentStateError,
    ConfigError,
    ConfigLoadError,
    ConfigValidationError,
)


def test_agent_error_basic():
    """测试 AgentError 基本功能"""
    error = AgentError("测试错误", error_code="TEST_ERROR", context={"key": "value"})
    
    assert error.message == "测试错误"
    assert error.error_code == "TEST_ERROR"
    assert error.context == {"key": "value"}
    assert "TEST_ERROR" in str(error)
    assert "测试错误" in str(error)


def test_agent_error_to_dict():
    """测试 AgentError 转换为字典"""
    error = AgentError("测试错误", error_code="TEST_ERROR", context={"key": "value"})
    error_dict = error.to_dict()
    
    assert error_dict["error_type"] == "AgentError"
    assert error_dict["message"] == "测试错误"
    assert error_dict["error_code"] == "TEST_ERROR"
    assert error_dict["context"] == {"key": "value"}


def test_model_load_error():
    """测试 ModelLoadError"""
    error = ModelLoadError("/path/to/model.pt", cause=Exception("文件不存在"))
    
    assert "无法加载模型" in error.message
    assert error.error_code == "MODEL_LOAD_FAILED"
    assert error.context["model_path"] == "/path/to/model.pt"
    assert "文件不存在" in error.context["cause"]


def test_inference_error():
    """测试 InferenceError"""
    error = InferenceError("/path/to/image.jpg", cause=Exception("内存不足"))
    
    assert "模型推理失败" in error.message
    assert error.error_code == "INFERENCE_FAILED"
    assert error.context["image_path"] == "/path/to/image.jpg"


def test_image_process_error():
    """测试 ImageProcessError"""
    error = ImageProcessError("resize", cause=Exception("无效尺寸"))
    
    assert "图像处理失败" in error.message
    assert error.error_code == "IMAGE_PROCESS_FAILED"
    assert error.context["operation"] == "resize"


def test_vector_store_error():
    """测试 VectorStoreError"""
    error = VectorStoreError("load", cause=Exception("文件损坏"))
    
    assert "向量存储操作失败" in error.message
    assert error.error_code == "VECTOR_STORE_FAILED"
    assert error.context["operation"] == "load"


def test_embedding_error():
    """测试 EmbeddingError"""
    long_text = "这是一段很长的文本" * 10
    error = EmbeddingError(long_text, cause=Exception("API 错误"))
    
    assert "嵌入生成失败" in error.message
    assert error.error_code == "EMBEDDING_FAILED"
    assert len(error.context["text_preview"]) <= 50


def test_retrieval_error():
    """测试 RetrievalError"""
    error = RetrievalError("水稻病害", cause=Exception("连接超时"))
    
    assert "知识库检索失败" in error.message
    assert error.error_code == "RETRIEVAL_FAILED"
    assert error.context["query"] == "水稻病害"


def test_token_limit_exceeded():
    """测试 TokenLimitExceeded"""
    error = TokenLimitExceeded(current_tokens=8000, max_tokens=10000, request_tokens=3000)
    
    assert "Token 限制超出" in error.message
    assert error.error_code == "TOKEN_LIMIT_EXCEEDED"
    assert error.context["current_tokens"] == 8000
    assert error.context["max_tokens"] == 10000
    assert error.context["request_tokens"] == 3000
    assert error.context["exceeded_by"] == 1000


def test_api_error():
    """测试 APIError"""
    error = APIError("OpenAI", status_code=500, cause=Exception("服务器错误"))
    
    assert "API 调用失败" in error.message
    assert error.error_code == "API_CALL_FAILED"
    assert error.context["api_name"] == "OpenAI"
    assert error.context["status_code"] == 500


def test_rate_limit_error():
    """测试 RateLimitError"""
    error = RateLimitError(retry_after=60)
    
    assert "API 速率限制超出" in error.message
    assert error.error_code == "RATE_LIMIT_EXCEEDED"
    assert error.context["retry_after"] == 60
    assert "60 秒后重试" in error.message


def test_model_not_found_error():
    """测试 ModelNotFoundError"""
    error = ModelNotFoundError("gpt-5")
    
    assert "模型未找到" in error.message
    assert error.error_code == "MODEL_NOT_FOUND"
    assert error.context["model_name"] == "gpt-5"


def test_execution_error():
    """测试 ExecutionError"""
    error = ExecutionError("detection_tool", "detect", cause=Exception("模型未加载"))
    
    assert "工具执行失败" in error.message
    assert error.error_code == "TOOL_EXECUTION_FAILED"
    assert error.context["tool_name"] == "detection_tool"
    assert error.context["operation"] == "detect"


def test_parameter_error():
    """测试 ParameterError"""
    error = ParameterError("detection_tool", "confidence", "float", "invalid")
    
    assert "参数错误" in error.message
    assert error.error_code == "PARAMETER_ERROR"
    assert error.context["tool_name"] == "detection_tool"
    assert error.context["parameter_name"] == "confidence"
    assert error.context["expected_type"] == "float"
    assert error.context["actual_value"] == "invalid"


def test_agent_not_found_error():
    """测试 AgentNotFoundError"""
    error = AgentNotFoundError("unknown_agent", ["detection", "knowledge"])
    
    assert "Agent 未找到" in error.message
    assert error.error_code == "AGENT_NOT_FOUND"
    assert error.context["agent_key"] == "unknown_agent"
    assert error.context["available_agents"] == ["detection", "knowledge"]


def test_flow_execution_error():
    """测试 FlowExecutionError"""
    error = FlowExecutionError("detection_flow", "step_2", cause=Exception("Agent 失败"))
    
    assert "Flow 执行失败" in error.message
    assert error.error_code == "FLOW_EXECUTION_FAILED"
    assert error.context["flow_name"] == "detection_flow"
    assert error.context["step"] == "step_2"


def test_agent_state_error():
    """测试 AgentStateError"""
    error = AgentStateError("detection_agent", "running", "idle")
    
    assert "Agent 状态错误" in error.message
    assert error.error_code == "AGENT_STATE_ERROR"
    assert error.context["agent_name"] == "detection_agent"
    assert error.context["current_state"] == "running"
    assert error.context["expected_state"] == "idle"


def test_config_load_error():
    """测试 ConfigLoadError"""
    error = ConfigLoadError("/path/to/config.toml", cause=Exception("文件不存在"))
    
    assert "配置加载失败" in error.message
    assert error.error_code == "CONFIG_LOAD_FAILED"
    assert error.context["config_path"] == "/path/to/config.toml"


def test_config_validation_error():
    """测试 ConfigValidationError"""
    error = ConfigValidationError("llm.api_key", "不能为空")
    
    assert "配置验证失败" in error.message
    assert error.error_code == "CONFIG_VALIDATION_FAILED"
    assert error.context["field_name"] == "llm.api_key"
    assert error.context["validation_error"] == "不能为空"


def test_exception_inheritance():
    """测试异常继承关系"""
    # 检测相关异常继承
    assert issubclass(DetectionError, AgentError)
    assert issubclass(ModelLoadError, DetectionError)
    assert issubclass(InferenceError, DetectionError)
    
    # RAG 相关异常继承
    assert issubclass(RAGError, AgentError)
    assert issubclass(VectorStoreError, RAGError)
    assert issubclass(EmbeddingError, RAGError)
    
    # LLM 相关异常继承
    assert issubclass(LLMError, AgentError)
    assert issubclass(TokenLimitExceeded, LLMError)
    assert issubclass(APIError, LLMError)
    
    # 工具相关异常继承
    assert issubclass(ToolError, AgentError)
    assert issubclass(ExecutionError, ToolError)
    assert issubclass(ParameterError, ToolError)
    
    # Flow 相关异常继承
    assert issubclass(FlowError, AgentError)
    assert issubclass(AgentNotFoundError, FlowError)
    assert issubclass(FlowExecutionError, FlowError)
    
    # 配置相关异常继承
    assert issubclass(ConfigError, AgentError)
    assert issubclass(ConfigLoadError, ConfigError)


def test_exception_catching():
    """测试异常捕获"""
    # 可以用基类捕获子类异常
    try:
        raise ModelLoadError("/path/to/model.pt")
    except DetectionError as e:
        assert isinstance(e, ModelLoadError)
    except Exception:
        pytest.fail("应该被 DetectionError 捕获")
    
    # 可以用 AgentError 捕获所有自定义异常
    try:
        raise TokenLimitExceeded(8000, 10000, 3000)
    except AgentError as e:
        assert isinstance(e, TokenLimitExceeded)
    except Exception:
        pytest.fail("应该被 AgentError 捕获")


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
