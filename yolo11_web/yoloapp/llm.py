# -*- coding: utf-8 -*-
"""
LLM 客户端

提供带重试机制的 LLM 调用功能。
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI, OpenAIError, APIError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

from yoloapp.schema import Message
from yoloapp.exceptions import LLMError, TokenLimitExceeded
from yoloapp.token_counter import TokenCounter
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """LLM 客户端（支持重试和 Token 计数）
    
    提供统一的 LLM 调用接口，支持：
    - 自动重试（使用 tenacity）
    - Token 计数和限制检查
    - 流式响应
    - 多配置支持
    
    Attributes:
        config_name: 配置名称
        config: LLM 配置
        client: OpenAI 客户端
        token_counter: Token 计数器
        total_tokens: 总 token 使用量
    """
    
    # 类级别的实例缓存（支持多配置）
    _instances: Dict[str, "LLMClient"] = {}
    
    def __new__(cls, config_name: str = "default"):
        """单例模式（每个配置一个实例）
        
        Args:
            config_name: 配置名称
            
        Returns:
            LLMClient 实例
        """
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[config_name] = instance
        return cls._instances[config_name]
    
    def __init__(self, config_name: str = "default"):
        """初始化 LLM 客户端
        
        Args:
            config_name: 配置名称
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self.config_name = config_name
        self.total_tokens = 0
        
        # 加载配置
        try:
            from yoloapp.config import get_config_manager
            config_manager = get_config_manager()
            
            # 获取 LLM 配置
            if hasattr(config_manager, 'llm'):
                llm_config = config_manager.llm
                
                # 根据配置名称选择配置
                if config_name == "zhipu":
                    self.config = {
                        "model": llm_config.zhipu_model,
                        "base_url": llm_config.zhipu_base_url,
                        "api_key": llm_config.zhipu_api_key,
                        "max_tokens": llm_config.max_tokens,
                        "temperature": llm_config.temperature,
                        "timeout": llm_config.timeout,
                    }
                elif config_name == "dashscope":
                    self.config = {
                        "model": llm_config.dashscope_model,
                        "base_url": llm_config.dashscope_base_url,
                        "api_key": llm_config.dashscope_api_key,
                        "max_tokens": llm_config.max_tokens,
                        "temperature": llm_config.temperature,
                        "timeout": llm_config.timeout,
                    }
                else:  # default
                    # 默认使用智谱
                    self.config = {
                        "model": llm_config.zhipu_model,
                        "base_url": llm_config.zhipu_base_url,
                        "api_key": llm_config.zhipu_api_key,
                        "max_tokens": llm_config.max_tokens,
                        "temperature": llm_config.temperature,
                        "timeout": llm_config.timeout,
                    }
            else:
                # 降级：使用环境变量
                import os
                self.config = {
                    "model": os.getenv("ZHIPU_MODEL", "glm-4-flash"),
                    "base_url": os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
                    "api_key": os.getenv("ZHIPU_API_KEY", ""),
                    "max_tokens": int(os.getenv("MAX_TOKENS", "2000")),
                    "temperature": float(os.getenv("TEMPERATURE", "0.7")),
                    "timeout": int(os.getenv("TIMEOUT", "60")),
                }
                logger.warning(f"使用环境变量配置 LLM 客户端")
        
        except Exception as e:
            logger.error(f"加载配置失败: {e}，使用默认配置")
            import os
            self.config = {
                "model": os.getenv("ZHIPU_MODEL", "glm-4-flash"),
                "base_url": os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/"),
                "api_key": os.getenv("ZHIPU_API_KEY", ""),
                "max_tokens": 2000,
                "temperature": 0.7,
                "timeout": 60,
            }
        
        # 创建 OpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=self.config["api_key"],
            base_url=self.config["base_url"],
            timeout=self.config["timeout"]
        )
        
        # 创建 Token 计数器
        self.token_counter = TokenCounter(self.config["model"])
        
        self._initialized = True
        logger.info(f"LLM 客户端初始化完成: {config_name} ({self.config['model']})")
    
    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
        before_sleep=before_sleep_log(logger, logger.level("WARNING").no),
        after=after_log(logger, logger.level("INFO").no)
    )
    async def ask(
        self,
        messages: List[Message] | List[Dict[str, Any]],
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        check_token_limit: bool = True,
        **kwargs
    ) -> str | AsyncIterator[str]:
        """发送请求到 LLM
        
        Args:
            messages: 消息列表（Message 对象或字典）
            stream: 是否使用流式响应
            tools: 工具列表（function calling）
            tool_choice: 工具选择策略
            check_token_limit: 是否检查 token 限制
            **kwargs: 其他参数
            
        Returns:
            响应文本或流式迭代器
            
        Raises:
            TokenLimitExceeded: Token 超限
            LLMError: LLM 调用失败
        """
        # 格式化消息
        formatted_messages = self._format_messages(messages)
        
        # Token 计数
        input_tokens = self.token_counter.count_messages(formatted_messages)
        logger.info(f"输入 Token 数: {input_tokens}")
        
        # 检查 token 限制
        if check_token_limit:
            max_tokens = self.config.get("max_tokens", 2000)
            is_within_limit, current_tokens = self.token_counter.check_limit(
                formatted_messages,
                max_tokens,
                reserve_tokens=500
            )
            
            if not is_within_limit:
                raise TokenLimitExceeded(
                    current_tokens=current_tokens,
                    max_tokens=max_tokens,
                    request_tokens=input_tokens
                )
        
        # 更新总 token 数
        self.total_tokens += input_tokens
        
        # 准备请求参数
        request_params = {
            "model": self.config["model"],
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "stream": stream,
        }
        
        # 添加 tools（如果有）
        if tools:
            request_params["tools"] = tools
            if tool_choice:
                request_params["tool_choice"] = tool_choice
        
        # 添加其他参数
        for key in ["max_tokens", "top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs:
                request_params[key] = kwargs[key]
        
        try:
            logger.debug(f"发送 LLM 请求: {request_params['model']}")
            
            # 发送请求
            response = await self.client.chat.completions.create(**request_params)
            
            # 处理响应
            if stream:
                return self._handle_stream(response)
            else:
                # 提取响应内容（兼容多种格式）
                content = self._extract_response_content(response)
                
                # 计算输出 token
                output_tokens = self.token_counter.count_text(content)
                self.total_tokens += output_tokens
                logger.info(f"输出 Token 数: {output_tokens}, 总计: {self.total_tokens}")
                
                return content
        
        except OpenAIError as e:
            logger.error(f"LLM API 错误: {e}")
            from yoloapp.exceptions import APIError as YoloAPIError
            raise YoloAPIError(
                api_name=self.config["model"],
                status_code=getattr(e, 'status_code', None),
                cause=e
            )
        
        except Exception as e:
            logger.error(f"LLM 调用异常: {e}", exc_info=True)
            raise LLMError(
                message=f"LLM 调用失败: {str(e)}",
                error_code="LLM_CALL_FAILED",
                context={"model": self.config["model"], "error": str(e)}
            )
    
    async def _handle_stream(self, response: AsyncIterator) -> AsyncIterator[str]:
        """处理流式响应
        
        Args:
            response: 流式响应迭代器
            
        Yields:
            响应文本片段
        """
        collected = []
        
        try:
            async for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    content = delta.content if delta.content else ""
                    
                    if content:
                        collected.append(content)
                        yield content
            
            # 计算输出 token
            full_content = "".join(collected)
            output_tokens = self.token_counter.count_text(full_content)
            self.total_tokens += output_tokens
            logger.info(f"流式输出 Token 数: {output_tokens}, 总计: {self.total_tokens}")
        
        except Exception as e:
            logger.error(f"流式响应处理失败: {e}")
            raise
    
    def _format_messages(
        self,
        messages: List[Message] | List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """格式化消息列表
        
        Args:
            messages: 消息列表
            
        Returns:
            格式化后的消息列表
        """
        formatted = []
        
        for msg in messages:
            if isinstance(msg, Message):
                # Message 对象转字典
                formatted.append(msg.to_dict())
            elif isinstance(msg, dict):
                # 已经是字典，直接使用
                formatted.append(msg)
            else:
                logger.warning(f"未知的消息类型: {type(msg)}")
        
        return formatted
    
    def reset_token_count(self) -> None:
        """重置 token 计数"""
        self.total_tokens = 0
        logger.info("Token 计数已重置")
    
    def get_token_stats(self) -> Dict[str, Any]:
        """获取 token 统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "config_name": self.config_name,
            "model": self.config["model"],
            "total_tokens": self.total_tokens,
            "token_counter": self.token_counter.get_stats()
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"LLMClient({self.config_name}, {self.config['model']})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"<LLMClient config={self.config_name} "
            f"model={self.config['model']} "
            f"tokens={self.total_tokens}>"
        )



    def _extract_response_content(self, response) -> str:
        """提取响应内容（兼容多种 API 格式）
        
        Args:
            response: API 响应对象
            
        Returns:
            响应文本内容
            
        Raises:
            LLMError: 无法提取内容
        """
        try:
            # 方法1: 标准 OpenAI 格式
            if hasattr(response, 'choices') and response.choices:
                if len(response.choices) > 0:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content = choice.message.content
                        if content:
                            return content
            
            # 方法2: 检查响应对象的其他属性
            if hasattr(response, 'content'):
                return response.content
            
            # 方法3: 转换为字典检查
            if hasattr(response, 'model_dump'):
                response_dict = response.model_dump()
            elif hasattr(response, 'dict'):
                response_dict = response.dict()
            elif isinstance(response, dict):
                response_dict = response
            else:
                response_dict = {}
            
            # 检查字典中的内容
            if response_dict:
                # 火山引擎可能的格式
                if 'data' in response_dict and isinstance(response_dict['data'], dict):
                    if 'content' in response_dict['data']:
                        return response_dict['data']['content']
                
                # 其他可能的格式
                if 'result' in response_dict:
                    return str(response_dict['result'])
                
                if 'output' in response_dict:
                    return str(response_dict['output'])
                
                # 检查 choices（即使为空也要检查）
                if 'choices' in response_dict and response_dict['choices']:
                    first_choice = response_dict['choices'][0]
                    if isinstance(first_choice, dict):
                        if 'message' in first_choice and 'content' in first_choice['message']:
                            return first_choice['message']['content']
                        if 'text' in first_choice:
                            return first_choice['text']
            
            # 方法4: 直接转字符串（最后的降级方案）
            response_str = str(response)
            logger.warning(f"无法从标准字段提取内容，使用字符串表示: {response_str[:200]}")
            
            # 如果响应太短或看起来像错误，抛出异常
            if len(response_str) < 10 or 'error' in response_str.lower():
                raise LLMError(
                    message="LLM 响应格式异常",
                    error_code="INVALID_RESPONSE_FORMAT",
                    context={"response": response_str[:500]}
                )
            
            return response_str
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"提取响应内容失败: {e}")
            logger.error(f"响应对象类型: {type(response)}")
            logger.error(f"响应对象属性: {dir(response)}")
            
            raise LLMError(
                message=f"无法提取 LLM 响应内容: {str(e)}",
                error_code="RESPONSE_EXTRACTION_FAILED",
                context={"error": str(e), "response_type": str(type(response))}
            )


# 工厂函数
def get_llm_client(config_name: str = "default") -> LLMClient:
    """获取 LLM 客户端实例
    
    Args:
        config_name: 配置名称（default, zhipu, dashscope）
        
    Returns:
        LLMClient 实例
    """
    return LLMClient(config_name)
