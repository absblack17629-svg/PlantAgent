# -*- coding: utf-8 -*-
"""
天气监测工具

提供天气信息查询和农业建议功能。
"""

from typing import Dict, Any

from .base import BaseTool, ToolResult
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class WeatherTool(BaseTool):
    """天气监测工具
    
    获取天气信息并提供农业建议。
    """
    
    name: str = "weather_forecast"
    description: str = "获取天气信息并提供农业建议"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "城市名或经纬度"
            }
        },
        "required": ["location"]
    }
    
    skill: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化天气工具"""
        super().__init__(**data)
        
        # 延迟导入避免循环依赖
        if self.skill is None:
            from skills.weather_skill import WeatherSkill
            self.skill = WeatherSkill()
        
        logger.info(f"初始化天气工具: {self.name}")
    
    async def execute(self, location: str, **kwargs) -> ToolResult:
        """查询天气信息
        
        Args:
            location: 城市名或经纬度
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 天气信息和农业建议
        """
        try:
            logger.info(f"查询天气: {location}")
            
            # 调用技能执行
            result = await self.skill.execute(location=location)
            
            # 检查技能返回结果
            if isinstance(result, dict):
                if result.get("success"):
                    return self.success_response(
                        data=result.get("output", result),
                        message="天气查询完成"
                    )
                else:
                    return self.fail_response(
                        error=result.get("error", "天气查询失败"),
                        error_code="SKILL_EXECUTION_FAILED"
                    )
            else:
                return self.success_response(
                    data=result,
                    message="天气查询完成"
                )
        
        except Exception as e:
            logger.error(f"天气查询失败: {e}", exc_info=True)
            return self.fail_response(
                error=f"天气查询失败: {str(e)}",
                error_code="WEATHER_QUERY_FAILED"
            )


# 工厂函数
def get_weather_tool() -> WeatherTool:
    """获取天气工具实例"""
    return WeatherTool()
