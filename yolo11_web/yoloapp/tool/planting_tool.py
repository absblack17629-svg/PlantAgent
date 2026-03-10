# -*- coding: utf-8 -*-
"""
种植规划工具

提供种植规划建议功能。
"""

from typing import Dict, Any

from .base import BaseTool, ToolResult
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class PlantingPlanTool(BaseTool):
    """种植规划工具
    
    根据土地情况和季节提供种植规划建议。
    """
    
    name: str = "planting_plan"
    description: str = "根据土地情况和季节提供种植规划建议"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "land_area": {
                "type": "number",
                "description": "土地面积（亩）"
            },
            "soil_type": {
                "type": "string",
                "description": "土壤类型（壤土、砂壤土、黏土、水田等）"
            },
            "location": {
                "type": "string",
                "description": "地理位置"
            },
            "season": {
                "type": "string",
                "description": "种植季节（春季、夏季、秋季、冬季）"
            }
        },
        "required": ["land_area", "soil_type", "season"]
    }
    
    skill: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化种植规划工具"""
        super().__init__(**data)
        
        # 延迟导入避免循环依赖
        if self.skill is None:
            from skills.planting_plan_skill import PlantingPlanSkill
            self.skill = PlantingPlanSkill()
        
        logger.info(f"初始化种植规划工具: {self.name}")
    
    async def execute(
        self,
        land_area: float,
        soil_type: str,
        season: str,
        location: str = "",
        **kwargs
    ) -> ToolResult:
        """执行种植规划
        
        Args:
            land_area: 土地面积（亩）
            soil_type: 土壤类型
            season: 种植季节
            location: 地理位置（可选）
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 规划结果
        """
        try:
            logger.info(f"执行种植规划: {land_area}亩 {soil_type} {season}")
            
            # 调用技能执行
            result = await self.skill.execute(
                land_area=land_area,
                soil_type=soil_type,
                location=location,
                season=season
            )
            
            # 检查技能返回结果
            if isinstance(result, dict):
                if result.get("success"):
                    return self.success_response(
                        data=result.get("output", result),
                        message="种植规划完成"
                    )
                else:
                    return self.fail_response(
                        error=result.get("error", "种植规划失败"),
                        error_code="SKILL_EXECUTION_FAILED"
                    )
            else:
                return self.success_response(
                    data=result,
                    message="种植规划完成"
                )
        
        except Exception as e:
            logger.error(f"种植规划失败: {e}", exc_info=True)
            return self.fail_response(
                error=f"种植规划失败: {str(e)}",
                error_code="PLANTING_PLAN_FAILED"
            )


# 工厂函数
def get_planting_plan_tool() -> PlantingPlanTool:
    """获取种植规划工具实例"""
    return PlantingPlanTool()
