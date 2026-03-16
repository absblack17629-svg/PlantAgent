# -*- coding: utf-8 -*-
"""
九节点智能体 - OpenManus风格重构版 v3 (续)
继承链: BaseAgent -> PlanAgent -> ToolAgent -> SkillAgent -> 具体Agent
"""

from .nine_node_v3 import (
    BaseAgent, AgentState, AgentStatus, StreamStep,
    IntentType, EmotionType, disease_name_map
)
from typing import Dict, List, Any, Optional
import time
import json


# ==================== PlanAgent ====================
class PlanAgent(BaseAgent):
    """计划制定Agent基类 - 负责制定执行计划"""
    
    def __init__(self, name: str, llm=None, skill_client=None):
        super().__init__(name, llm, skill_client)
        self.system_prompt = "你是一个任务规划专家，负责制定执行计划。"
    
    def create_plan(self, state: AgentState) -> List[Dict]:
        """创建执行计划 - 子类可重写"""
        return []
    
    async def process(self, state: AgentState) -> AgentState:
        """处理流程：制定计划"""
        start_time = time.time()
        self.status = AgentStatus.RUNNING
        
        try:
            # 记录输入
            input_data = f"用户输入: {state.user_input[:50]}..., 意图: {state.intent.value}"
            
            # 创建计划
            state.plan = self.create_plan(state)
            
            # 生成输出
            plan_summary = f"制定计划: {len(state.plan)} 个步骤"
            for i, step in enumerate(state.plan[:3], 1):  # 只显示前3步
                plan_summary += f"\n  步骤{i}: {step.get('skill', 'unknown')}.{step.get('action', 'unknown')}"
            
            self.status = AgentStatus.SUCCESS
            output_data = plan_summary
            
            # 记录步骤
            step = self._create_step(
                step_name="制定计划",
                input_data=input_data,
                output_data=output_data,
                start_time=start_time
            )
            state.add_step(step)
            state.trace.append(f"[{self.name}] Created plan with {len(state.plan)} steps")
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            error_msg = f"计划制定失败: {str(e)}"
            state.trace.append(f"[{self.name}] Error: {error_msg}")
            
            step = self._create_step(
                step_name="制定计划",
                input_data=state.user_input,
                output_data=error_msg,
                start_time=start_time
            )
            state.add_step(step)
        
        return state


# ==================== ToolAgent ====================
class ToolAgent(PlanAgent):
    """工具调用Agent基类 - 负责调用具体技能"""
    
    def __init__(self, name: str, llm=None, skill_client=None):
        super().__init__(name, llm, skill_client)
        self.system_prompt = "你是一个工具执行专家，负责调用各种技能。"
    
    def should_use_react(self, state: AgentState) -> bool:
        """是否使用ReAct模式 - 子类可重写"""
        return False
    
    def get_required_skills(self, state: AgentState) -> List[str]:
        """获取需要的技能列表 - 子类可重写"""
        return []
    
    async def execute_tool(self, tool: Dict, state: AgentState) -> Dict:
        """执行单个工具"""
        skill = tool.get("skill", "")
        action = tool.get("action", "")
        
        if not skill or skill == "none" or not self.skill_client:
            return {"skill": skill, "action": action, "result": "skip", "success": True}
        
        try:
            # 根据技能类型构建参数
            params = self._build_params(skill, action, state)
            
            # 执行技能
            result = await self.skill_client.call_capability(skill, action, **params)
            
            return {
                "skill": skill,
                "action": action,
                "result": str(result),
                "success": True
            }
        except Exception as e:
            return {
                "skill": skill,
                "action": action,
                "error": str(e),
                "success": False
            }
    
    def _build_params(self, skill: str, action: str, state: AgentState) -> Dict:
        """构建技能调用参数"""
        params = {}
        
        if skill == "DetectionSkill":
            if state.image_path:
                params["image_path"] = state.image_path
        
        elif skill == "KnowledgeSkill":
            if action == "query_knowledge":
                params["question"] = state.user_input
            elif action == "analyze_detection":
                params["question"] = state.user_input
                # 从之前的tool_results中获取detections
                detections_str = "[]"
                for prev_result in state.tool_results:
                    if prev_result.get("skill") == "DetectionSkill" and prev_result.get("success"):
                        result_content = prev_result.get("result", "")
                        if result_content and "检测到" in result_content:
                            detections_str = result_content
                            break
                params["detections"] = detections_str
        
        elif skill == "MemorySkill":
            params["task_description"] = state.user_input
        
        else:
            params["task_description"] = state.user_input
        
        return params
    
    async def process(self, state: AgentState) -> AgentState:
        """处理流程：执行计划中的工具"""
        start_time = time.time()
        self.status = AgentStatus.RUNNING
        
        try:
            input_data = f"计划步骤: {len(state.plan)} 个, 意图: {state.intent.value}"
            
            # 执行计划中的每个工具
            for i, tool in enumerate(state.plan):
                tool_result = await self.execute_tool(tool, state)
                state.tool_results.append(tool_result)
                state.trace.append(f"[{self.name}] Executed {tool.get('skill', 'none')}: {tool_result.get('success')}")
            
            output_data = f"执行完成: {len(state.tool_results)} 个工具调用"
            self.status = AgentStatus.SUCCESS
            
            step = self._create_step(
                step_name="执行工具",
                input_data=input_data,
                output_data=output_data,
                start_time=start_time
            )
            state.add_step(step)
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            error_msg = f"工具执行失败: {str(e)}"
            state.trace.append(f"[{self.name}] Error: {error_msg}")
            
            step = self._create_step(
                step_name="执行工具",
                input_data=state.user_input,
                output_data=error_msg,
                start_time=start_time
            )
            state.add_step(step)
        
        return state


print("[OK] PlanAgent 和 ToolAgent 定义完成")
