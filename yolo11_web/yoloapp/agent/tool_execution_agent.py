# -*- coding: utf-8 -*-
"""
节点6: 工具执行 Agent
负责根据执行计划调度技能系统
"""

from typing import Dict, List
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError, ToolError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class ToolExecutionAgent(BaseAgent):
    """
    工具执行 Agent
    
    职责:
    - 执行工具调用计划
    - 处理工具调用失败
    - 支持重试机制
    """
    
    def __init__(self, skill_client=None, max_retries: int = 2):
        super().__init__(
            name="ToolExecutionAgent",
            role=AgentRole.EXECUTOR,
            description="负责根据执行计划调度技能系统"
        )
        self.skill_client = skill_client
        self.max_retries = max_retries
    
    async def step(self) -> str:
        """
        执行工具调用步骤
        
        Returns:
            执行结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始执行工具...")
            
            # 1. 获取执行计划
            plan = self.memory.metadata.get("plan", [])
            
            if not plan:
                result = "⏭️ 跳过：无执行计划"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
                logger.info(f"[{self.name}] {result}")
                return result
            
            # 2. 执行所有工具
            tool_results = []
            for idx, tool in enumerate(plan):
                result = await self._execute_with_retry(tool, idx)
                tool_results.append(result)
                
                # 立即更新 metadata，让后续工具可以使用前面工具的结果
                self.memory.metadata["tool_results"] = tool_results.copy()
            
            # 3. 保存最终结果
            self.memory.metadata["tool_results"] = tool_results
            
            # 4. 生成摘要
            success_count = sum(1 for r in tool_results if r.get("success"))
            total_count = len(tool_results)
            summary = f"工具执行完成: {success_count}/{total_count} 成功"
            
            self.memory.add_message(Message(
                role="system",
                content=summary
            ))
            
            logger.info(f"[{self.name}] {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"工具执行失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    async def _execute_with_retry(self, tool: Dict, tool_index: int) -> Dict:
        """
        带重试机制的工具执行
        
        Args:
            tool: 工具定义
            tool_index: 工具索引
            
        Returns:
            执行结果字典
        """
        skill = tool.get("skill", "")
        action = tool.get("action", "")
        
        # 跳过不需要工具的步骤
        if skill == "none":
            return {
                "skill": skill,
                "action": action,
                "result": "skip",
                "success": True,
                "retry_count": 0
            }
        
        # 构建参数
        params = self._build_params(skill, action)
        
        # 重试循环
        for retry_count in range(self.max_retries + 1):
            try:
                if not self.skill_client:
                    # 无 skill_client 时返回模拟结果
                    return {
                        "skill": skill,
                        "action": action,
                        "result": f"Mock execution: {skill}.{action}",
                        "success": True,
                        "retry_count": retry_count
                    }
                
                # 调用技能
                result = await self.skill_client.call_capability(skill, action, **params)
                
                # 成功返回
                logger.info(f"[{self.name}] 工具执行成功: {skill}.{action}")
                return {
                    "skill": skill,
                    "action": action,
                    "result": str(result),
                    "success": True,
                    "retry_count": retry_count
                }
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"[{self.name}] 重试 {retry_count}/{self.max_retries}: {error_msg}")
                
                # 如果还有重试次数，继续
                if retry_count < self.max_retries:
                    continue
                
                # 重试次数用完，返回失败
                logger.error(f"[{self.name}] 工具执行失败: {skill}.{action}")
                return {
                    "skill": skill,
                    "action": action,
                    "error": error_msg,
                    "success": False,
                    "retry_count": retry_count,
                    "fail_reason": f"重试{self.max_retries}次后仍失败"
                }
        
        # 理论上不会到达这里
        return {
            "skill": skill,
            "action": action,
            "error": "未知错误",
            "success": False,
            "retry_count": self.max_retries
        }
    
    def _build_params(self, skill: str, action: str) -> Dict:
        """构建技能调用参数"""
        params = {}
        
        # 获取必要信息
        user_input = self._get_user_input()
        image_path = self.memory.metadata.get("image_path")
        tool_results = self.memory.metadata.get("tool_results", [])
        
        if skill == "DetectionSkill" and image_path:
            params["image_path"] = image_path
        elif skill == "KnowledgeSkill":
            if action == "query_knowledge":
                params["question"] = user_input
            elif action == "analyze_detection":
                params["question"] = user_input
                # 获取检测结果
                for result in tool_results:
                    if result.get("skill") == "DetectionSkill" and result.get("success"):
                        params["detections"] = result.get("result", "")
                        break
        elif skill == "MemorySkill":
            params["task_description"] = user_input
        else:
            params["task_description"] = user_input
        
        return params
    
    def _get_user_input(self) -> str:
        """从 Memory 中获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""
