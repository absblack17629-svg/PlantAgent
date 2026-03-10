# -*- coding: utf-8 -*-
"""
智能灌溉工具

提供灌溉决策建议功能。
"""

from typing import Dict, Any, Optional

from .base import BaseTool, ToolResult
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class IrrigationTool(BaseTool):
    """智能灌溉工具
    
    根据作物需求和天气情况提供灌溉建议。
    """
    
    name: str = "irrigation_advice"
    description: str = "根据作物需求和天气情况提供灌溉建议"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "crop_type": {
                "type": "string",
                "description": "作物类型（水稻、玉米、小麦、大豆等）"
            },
            "growth_stage": {
                "type": "string",
                "description": "生长阶段（seedling/tillering/heading/ripening等）"
            },
            "soil_moisture": {
                "type": "number",
                "description": "当前土壤湿度（百分比，0-100）"
            },
            "weather_forecast": {
                "type": "object",
                "description": "天气预报数据（可选）"
            },
            "last_irrigation": {
                "type": "string",
                "description": "上次灌溉时间（ISO格式，可选）"
            }
        },
        "required": ["crop_type", "growth_stage", "soil_moisture"]
    }
    
    skill: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化灌溉工具"""
        super().__init__(**data)
        
        # 延迟导入避免循环依赖
        if self.skill is None:
            from skills.irrigation_skill import IrrigationSkill
            self.skill = IrrigationSkill()
        
        logger.info(f"初始化灌溉工具: {self.name}")
    
    async def execute(
        self,
        crop_type: str,
        growth_stage: str,
        soil_moisture: float,
        weather_forecast: Optional[Dict] = None,
        last_irrigation: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        """执行灌溉决策
        
        Args:
            crop_type: 作物类型
            growth_stage: 生长阶段
            soil_moisture: 当前土壤湿度
            weather_forecast: 天气预报数据（可选）
            last_irrigation: 上次灌溉时间（可选）
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 灌溉建议
        """
        try:
            logger.info(f"执行灌溉决策: {crop_type} {growth_stage} 湿度{soil_moisture}%")
            
            # 调用技能执行
            result = await self.skill.execute(
                crop_type=crop_type,
                growth_stage=growth_stage,
                soil_moisture=soil_moisture,
                weather_forecast=weather_forecast or {},
                last_irrigation=last_irrigation
            )
            
            # 检查技能返回结果
            if isinstance(result, dict):
                if result.get("success"):
                    return self.success_response(
                        data=result.get("output", result),
                        message="灌溉决策完成"
                    )
                else:
                    return self.fail_response(
                        error=result.get("error", "灌溉决策失败"),
                        error_code="SKILL_EXECUTION_FAILED"
                    )
            else:
                return self.success_response(
                    data=result,
                    message="灌溉决策完成"
                )
        
        except Exception as e:
            logger.error(f"灌溉决策失败: {e}", exc_info=True)
            return self.fail_response(
                error=f"灌溉决策失败: {str(e)}",
                error_code="IRRIGATION_DECISION_FAILED"
            )


# 工厂函数
def get_irrigation_tool() -> IrrigationTool:
    """获取灌溉工具实例"""
    return IrrigationTool()
