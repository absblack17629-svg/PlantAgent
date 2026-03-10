# -*- coding: utf-8 -*-
"""
节点7: 结果验证 Agent
负责验证工具执行结果
"""

from typing import Dict, List
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class ResultValidationAgent(BaseAgent):
    """
    结果验证 Agent
    
    职责:
    - 验证工具执行结果
    - 统计成功率
    - 识别失败原因
    """
    
    def __init__(self):
        super().__init__(
            name="ResultValidationAgent",
            role=AgentRole.VALIDATOR,
            description="负责验证工具执行结果"
        )
    
    async def step(self) -> str:
        """
        执行结果验证步骤
        
        Returns:
            验证结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始验证结果...")
            
            # 1. 获取工具执行结果
            tool_results = self.memory.metadata.get("tool_results", [])
            
            if not tool_results:
                result = "⏭️ 跳过：无工具执行结果"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
                logger.info(f"[{self.name}] {result}")
                return result
            
            # 2. 验证结果
            validation = self._validate_results(tool_results)
            
            # 3. 保存验证结果
            self.memory.metadata["result_validation"] = validation
            
            # 4. 生成摘要
            success_rate = validation["success_rate"] * 100
            summary = f"结果验证: {validation['success_count']}/{validation['total']} 成功 ({success_rate:.0f}%)"
            
            if validation["issues"]:
                issues_preview = "; ".join(validation["issues"][:3])
                summary += f"\n问题: {issues_preview}"
            
            self.memory.add_message(Message(
                role="system",
                content=summary
            ))
            
            logger.info(f"[{self.name}] {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"结果验证失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    def _validate_results(self, results: List[Dict]) -> Dict:
        """
        验证执行结果
        
        Args:
            results: 工具执行结果列表
            
        Returns:
            验证结果字典
        """
        validation = {
            "success_count": 0,
            "fail_count": 0,
            "total": len(results),
            "success_rate": 0.0,
            "issues": []
        }
        
        for result in results:
            if result.get("success"):
                validation["success_count"] += 1
            else:
                validation["fail_count"] += 1
                error = result.get("error", "未知错误")
                skill = result.get("skill", "unknown")
                validation["issues"].append(f"{skill}: {error}")
        
        if validation["total"] > 0:
            validation["success_rate"] = validation["success_count"] / validation["total"]
        
        return validation
