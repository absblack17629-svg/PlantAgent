# -*- coding: utf-8 -*-
"""
工具基类

提供所有工具的基础接口和通用功能。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from yoloapp.schema import ToolResult, ToolParameter
from yoloapp.exceptions import ToolError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class BaseTool(ABC, BaseModel):
    """工具基类
    
    提供工具的基础功能，包括：
    - 统一的执行接口
    - 参数验证
    - 错误处理
    - 结果封装
    
    子类需要实现：
    - execute() 方法：定义具体的工具执行逻辑
    
    Attributes:
        name: 工具名称
        description: 工具描述
        parameters: 参数定义（JSON Schema 格式）
        metadata: 额外元数据
    """
    
    # 核心属性
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: Optional[Dict[str, Any]] = Field(None, description="参数 schema")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # 允许额外字段
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具（子类实现）
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 工具执行结果
            
        Raises:
            ToolError: 工具执行失败
            
        Example:
            async def execute(self, image_path: str) -> ToolResult:
                result = await self.detect(image_path)
                return self.success_response(result)
        """
        raise NotImplementedError("子类必须实现 execute() 方法")
    
    async def __call__(self, **kwargs) -> ToolResult:
        """调用工具
        
        提供便捷的调用方式，自动处理异常。
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            ToolResult: 工具执行结果
            
        Example:
            result = await tool(image_path="test.jpg")
        """
        try:
            logger.info(f"执行工具: {self.name}")
            logger.debug(f"工具参数: {kwargs}")
            
            # 验证参数
            self._validate_parameters(kwargs)
            
            # 执行工具
            result = await self.execute(**kwargs)
            
            logger.info(f"工具 {self.name} 执行成功")
            return result
            
        except ToolError as e:
            # 工具错误直接返回
            logger.error(f"工具 {self.name} 执行失败: {e.message}")
            return self.fail_response(e.message, error_code=e.error_code)
            
        except Exception as e:
            # 其他异常包装为 ToolError
            logger.error(f"工具 {self.name} 执行异常: {e}")
            return self.fail_response(
                f"工具执行异常: {str(e)}",
                error_code="TOOL_EXECUTION_ERROR"
            )
    
    def _validate_parameters(self, kwargs: Dict[str, Any]) -> None:
        """验证参数
        
        Args:
            kwargs: 传入的参数
            
        Raises:
            ToolError: 参数验证失败
        """
        if not self.parameters:
            return
        
        # 检查必需参数
        required_params = self.parameters.get("required", [])
        for param in required_params:
            if param not in kwargs:
                raise ToolError(
                    message=f"缺少必需参数: {param}",
                    error_code="MISSING_PARAMETER",
                    context={"tool": self.name, "parameter": param}
                )
        
        # 检查参数类型（简单验证）
        properties = self.parameters.get("properties", {})
        for param_name, param_value in kwargs.items():
            if param_name in properties:
                expected_type = properties[param_name].get("type")
                if expected_type:
                    self._check_type(param_name, param_value, expected_type)
    
    def _check_type(self, param_name: str, value: Any, expected_type: str) -> None:
        """检查参数类型
        
        Args:
            param_name: 参数名
            value: 参数值
            expected_type: 期望类型
            
        Raises:
            ToolError: 类型不匹配
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type and not isinstance(value, expected_python_type):
            raise ToolError(
                message=f"参数 {param_name} 类型错误，期望 {expected_type}",
                error_code="INVALID_PARAMETER_TYPE",
                context={
                    "tool": self.name,
                    "parameter": param_name,
                    "expected_type": expected_type,
                    "actual_type": type(value).__name__
                }
            )
    
    def to_param(self) -> Dict[str, Any]:
        """转换为 function calling 格式
        
        Returns:
            符合 OpenAI function calling 格式的字典
            
        Example:
            {
                "type": "function",
                "function": {
                    "name": "detect_objects",
                    "description": "检测图片中的对象",
                    "parameters": {
                        "type": "object",
                        "properties": {...},
                        "required": [...]
                    }
                }
            }
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters or {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    
    def success_response(
        self,
        data: Any,
        message: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """创建成功响应
        
        Args:
            data: 输出数据
            message: 可选的消息
            **kwargs: 额外的元数据
            
        Returns:
            ToolResult: 成功的工具结果
            
        Example:
            return self.success_response(
                data={"count": 5, "objects": [...]},
                message="检测完成"
            )
        """
        metadata = {
            "tool": self.name,
            **kwargs
        }
        
        if message:
            metadata["message"] = message
        
        return ToolResult(
            output=data,
            success=True,
            metadata=metadata
        )
    
    def fail_response(
        self,
        error: str,
        error_code: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """创建失败响应
        
        Args:
            error: 错误信息
            error_code: 错误码
            **kwargs: 额外的元数据
            
        Returns:
            ToolResult: 失败的工具结果
            
        Example:
            return self.fail_response(
                error="文件不存在",
                error_code="FILE_NOT_FOUND"
            )
        """
        metadata = {
            "tool": self.name,
            **kwargs
        }
        
        if error_code:
            metadata["error_code"] = error_code
        
        return ToolResult(
            error=error,
            success=False,
            metadata=metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            字典格式的工具信息
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        """详细表示"""
        return f"<{self.__class__.__name__} name={self.name}>"
