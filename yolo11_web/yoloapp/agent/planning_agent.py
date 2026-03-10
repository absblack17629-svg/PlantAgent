# -*- coding: utf-8 -*-
"""
节点4: 工具规划 Agent
负责根据用户意图制定执行计划
"""

from typing import Dict, List, Optional
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class PlanningAgent(BaseAgent):
    """
    工具规划 Agent
    
    职责:
    - 分析用户意图
    - 制定工具调用计划
    - 确定执行顺序
    """
    
    def __init__(self):
        super().__init__(
            name="PlanningAgent",
            role=AgentRole.PLANNER,
            description="负责根据用户意图制定执行计划"
        )
    
    async def step(self) -> str:
        """
        执行规划步骤
        
        Returns:
            规划结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始制定执行计划...")
            
            # 1. 获取意图
            intent = self.memory.metadata.get("intent", "chat")
            image_path = self.memory.metadata.get("image_path")
            
            # 2. 根据意图制定计划
            plan = self._create_plan(intent, image_path)
            
            # 3. 保存计划到 metadata
            self.memory.metadata["plan"] = plan
            
            # 4. 记录到 Memory
            plan_summary = self._format_plan(plan)
            self.memory.add_message(Message(
                role="system",
                content=f"执行计划已制定:\n{plan_summary}"
            ))
            
            logger.info(f"[{self.name}] 计划制定完成: {len(plan)} 个步骤")
            
            return plan_summary
            
        except Exception as e:
            error_msg = f"计划制定失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    def _create_plan(self, intent: str, image_path: Optional[str]) -> List[Dict]:
        """
        根据意图创建执行计划
        
        Args:
            intent: 用户意图
            image_path: 图片路径
            
        Returns:
            执行计划列表
        """
        plan = []
        
        if intent == "detect":
            # 检测意图：检测图片 + 分析结果
            if image_path:
                plan.append({
                    "skill": "DetectionSkill",
                    "action": "detect_objects",
                    "reason": "用户要求检测图片中的病害"
                })
            plan.append({
                "skill": "KnowledgeSkill",
                "action": "analyze_detection",
                "reason": "分析检测结果并提供建议"
            })
        
        elif intent == "query":
            # 查询意图：查询知识库
            plan.append({
                "skill": "KnowledgeSkill",
                "action": "query_knowledge",
                "reason": "用户查询农业知识"
            })
        
        elif intent in ["greet", "goodbye"]:
            # 问候/告别意图：无需调用技能
            plan.append({
                "skill": "none",
                "action": intent,
                "reason": f"{intent}不需要工具调用"
            })
        
        else:
            # 默认聊天意图
            plan.append({
                "skill": "KnowledgeSkill",
                "action": "query_knowledge",
                "reason": "尝试从知识库获取答案"
            })
        
        return plan
    
    def _format_plan(self, plan: List[Dict]) -> str:
        """格式化计划为可读字符串"""
        lines = [f"共 {len(plan)} 个步骤:"]
        for i, step in enumerate(plan, 1):
            skill = step.get("skill", "unknown")
            action = step.get("action", "unknown")
            reason = step.get("reason", "")
            lines.append(f"  步骤{i}: {skill}.{action} - {reason}")
        return "\n".join(lines)
