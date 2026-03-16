# -*- coding: utf-8 -*-
"""
PlantAgent - 单一智能 Agent

基于 ReAct 模式，一个 Agent 完成所有任务：
1. 理解用户意图
2. 选择合适工具
3. 执行工具
4. 生成响应
"""

from typing import Dict, List, Any, Optional
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class PlantAgent(BaseAgent):
    """
    单一智能 Agent

    一个 Agent 替代多个专门 Agent：
    - IntentAgent (意图识别)
    - PlanningAgent (工具规划)
    - RAGAgent (知识检索)
    - ToolExecutionAgent (工具执行)
    - ResponseAgent (响应生成)

    工作流程（ReAct 模式）：
    1. Reason: 分析用户输入，决定下一步
    2. Act: 执行工具
    3. Observe: 观察结果
    4. 重复直到完成
    """

    def __init__(self, max_iterations: int = 5):
        super().__init__(
            name="PlantAgent",
            role=AgentRole.GENERAL,
            description="单一智能 Agent，自动完成所有任务",
        )
        self.max_iterations = max_iterations

    async def step(self) -> str:
        """
        执行任务（ReAct 循环）

        Returns:
            最终响应
        """
        try:
            logger.info(f"[{self.name}] 开始处理任务...")

            user_input = self._get_user_input()
            image_path = self.memory.metadata.get("image_path")

            # ReAct 循环
            results = await self._react_loop(user_input, image_path)

            # 生成最终响应
            final_response = await self._generate_response(results, user_input)

            self.memory.metadata["final_response"] = final_response
            self.memory.metadata["execution_results"] = results

            logger.info(f"[{self.name}] 任务完成")
            return final_response

        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            return f"抱歉，处理过程中出现错误：{str(e)}"

    async def _react_loop(
        self, user_input: str, image_path: Optional[str]
    ) -> List[Dict]:
        """ReAct 循环：理解 → 选择工具 → 执行 → 观察 → 重复"""

        results = []
        context = ""

        for iteration in range(self.max_iterations):
            # 1. Reason: 让 LLM 决定下一步
            action = await self._reason(user_input, image_path, context, iteration)

            # 2. 检查是否结束
            if action.get("type") == "finish":
                logger.info(f"[{self.name}] 任务完成，停止循环")
                break

            # 3. Act: 执行工具
            if action.get("type") == "tool":
                tool_name = action.get("tool")
                params = action.get("params", {})

                result = await self._execute_tool(tool_name, params)

                results.append(
                    {
                        "iteration": iteration + 1,
                        "tool": tool_name,
                        "params": params,
                        "result": result,
                    }
                )

                # 4. Observe: 更新上下文
                context += f"\n[工具 {tool_name} 返回]: {str(result)[:200]}"

                logger.info(f"[{self.name}] 迭代 {iteration + 1}: {tool_name} → 成功")

        return results

    async def _reason(
        self, user_input: str, image_path: Optional[str], context: str, iteration: int
    ) -> Dict:
        """让 LLM 分析情况，决定下一步"""

        try:
            from yoloapp.llm import get_llm_client
            from yoloapp.tool.langchain_tools import get_all_tools

            llm = get_llm_client()
            tools = get_all_tools()

            # 构建工具描述
            tools_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools])

            prompt = f"""你是一个智能助手，负责理解用户需求并选择合适的工具来完成任务。

用户输入: {user_input}
图片路径: {image_path or "无"}

已执行的结果:
{context if context else "(无)"}

可用工具:
{tools_desc}

请决定下一步做什么：

返回 JSON 格式：
{{
    "type": "tool" 或 "finish",
    "reason": "你的推理",
    "tool": "工具名（如果是 tool）",
    "params": {{"参数": "值"}}
}}

规则：
- 如果任务需要工具，返回 {{
    "type": "tool", 
    "reason": "...", 
    "tool": "工具名", 
    "params": {{...}}
  }}
- 如果任务已完成或不需要更多工具，返回 {{
    "type": "finish", 
    "reason": "..."
  }}
- 工具参数 image_path 如果有图片则传图片路径"""

            response = await llm.ask(
                [Message.system_message(prompt), Message.user_message("请决定下一步")]
            )

            content = (
                response.content if hasattr(response, "content") else str(response)
            )
            return self._parse_json(content) or {"type": "finish", "reason": "解析失败"}

        except Exception as e:
            logger.warning(f"推理失败: {e}")
            return {"type": "finish", "reason": f"推理出错: {e}"}

    async def _execute_tool(self, tool_name: str, params: Dict) -> str:
        """执行工具"""

        try:
            from yoloapp.tool.langchain_tools import get_all_tools

            tools = get_all_tools()
            tool_dict = {t.name: t for t in tools}

            if tool_name not in tool_dict:
                return f"错误：工具 {tool_name} 不存在"

            tool = tool_dict[tool_name]
            result = await tool.ainvoke(params)

            return str(result)

        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            return f"执行失败: {str(e)}"

    async def _generate_response(self, results: List[Dict], user_input: str) -> str:
        """生成最终响应"""

        try:
            from yoloapp.llm import get_llm_client

            llm = get_llm_client()

            # 汇总所有工具结果
            all_results = ""
            for r in results:
                all_results += f"\n{r.get('tool', 'unknown')}: {r.get('result', '')}"

            # 如果有工具结果，用 LLM 润色
            if all_results:
                prompt = f"""请将以下工具返回的结果整理成友好的回复：

用户问题: {user_input}

工具结果:
{all_results}

要求：
1. 用第一人称"我"来回答
2. 语言亲切自然
3. 包含关键信息
4. 适当使用 emoji"""

                response = await llm.ask(
                    [Message.system_message(prompt), Message.user_message("请生成回复")]
                )

                return (
                    response.content if hasattr(response, "content") else str(response)
                )
            else:
                # 没有工具结果，直接对话
                prompt = f"""请回答用户的问题：

用户问题: {user_input}

请用友好、专业的语气回答。"""

                response = await llm.ask(
                    [Message.system_message(prompt), Message.user_message("请回答")]
                )

                return (
                    response.content if hasattr(response, "content") else str(response)
                )

        except Exception as e:
            logger.error(f"响应生成失败: {e}")
            # 返回原始结果
            return "\n".join([r.get("result", "") for r in results]) or "处理完成"

    def _get_user_input(self) -> str:
        """获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""

    def _parse_json(self, content: str) -> Optional[Dict]:
        """解析 JSON"""
        import json

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except:
            return None
