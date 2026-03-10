# -*- coding: utf-8 -*-
"""
确认Agent

负责询问用户是否需要查询相关知识：
1. 检查检测结果
2. 询问用户是否需要查询防治方案/种植规划/灌溉策略
3. 记录用户确认状态
4. 根据用户选择调整后续流程
"""

from typing import Dict, Any, List
from yoloapp.agent.base import BaseAgent
from yoloapp.schema import AgentRole, Memory, Message
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class ConfirmationAgent(BaseAgent):
    """确认Agent - 询问用户是否需要相关知识"""

    def __init__(self, **kwargs):
        super().__init__(
            name="ConfirmationAgent",
            role=AgentRole.VALIDATOR,  # 使用现有的VALIDATOR角色
            description="负责询问用户是否需要查询相关知识",
            **kwargs,
        )

    async def step(self) -> str:
        """
        执行确认步骤

        流程:
        1. 检查是否有检测结果
        2. 如果没有检测结果，直接完成
        3. 如果有检测结果，询问用户是否需要相关知识
        4. 设置确认状态，等待用户响应

        Returns:
            确认提示文本或完成状态
        """
        logger.info("开始确认步骤...")

        # 1. 检查是否有检测结果
        detection_result = self._get_detection_result()
        if not detection_result:
            logger.info("未找到检测结果，跳过确认步骤")
            self.mark_finished()
            return "无需确认"

        # 2. 检查是否应该跳过确认
        if self._should_skip_confirmation(detection_result):
            logger.info("跳过确认步骤，自动确认或无需确认")
            # _should_skip_confirmation 方法已经设置了 user_confirmed
            self.mark_finished()
            return "跳过确认"

        # 2. 检查是否已经确认
        if self.memory.metadata.get("user_confirmed") is not None:
            logger.info(f"用户已确认: {self.memory.metadata.get('user_confirmed')}")
            self.mark_finished()
            return "确认状态已设置"

        # 3. 检查是否正在等待确认
        if self.memory.metadata.get("waiting_confirmation", False):
            logger.info("正在等待用户确认，检查用户响应...")
            user_response = self._get_user_response()
            confirmation_status = self._parse_user_confirmation(user_response)

            if confirmation_status is None:
                # 用户未明确确认或拒绝，继续等待
                logger.info("用户响应不明确，继续等待确认")
                return self.memory.metadata.get(
                    "confirmation_prompt", "请确认是否查询相关知识"
                )

            # 设置确认状态
            self.memory.metadata["user_confirmed"] = confirmation_status
            self.memory.metadata["waiting_confirmation"] = False

            logger.info(f"用户确认状态: {confirmation_status}")
            self.mark_finished()
            return f"用户{'确认' if confirmation_status else '拒绝'}查询相关知识"

        # 4. 第一次执行，生成确认请求
        logger.info("生成确认请求...")
        confirmation_prompt = self._generate_confirmation_prompt(detection_result)

        # 设置等待确认状态
        self.memory.metadata["waiting_confirmation"] = True
        self.memory.metadata["confirmation_prompt"] = confirmation_prompt

        logger.info("确认请求已生成，等待用户响应")
        return confirmation_prompt

    def _get_detection_result(self) -> Dict[str, Any]:
        """获取检测结果"""
        # 从tool_results中查找检测结果
        tool_results = self.memory.metadata.get("tool_results", [])
        for result in tool_results:
            if result.get("skill") == "DetectionSkill" and result.get("success"):
                return result.get("result", {})

        # 或者直接从metadata中获取
        return self.memory.metadata.get("detection_result", {})

    def _get_user_response(self) -> str:
        """获取用户的最新响应"""
        # 获取最后一条用户消息
        for message in reversed(self.memory.messages):
            if message.role == "user":
                return message.content

        return ""

    def _parse_user_confirmation(self, user_response: str) -> bool:
        """
        解析用户确认响应

        Args:
            user_response: 用户响应文本

        Returns:
            True - 确认, False - 拒绝, None - 不明确
        """
        if not user_response:
            return None

        # 确认关键词
        confirm_keywords = [
            "是",
            "确认",
            "需要",
            "要",
            "好的",
            "可以",
            "行",
            "ok",
            "yes",
            "y",
            "同意",
        ]
        # 拒绝关键词
        reject_keywords = [
            "不",
            "不用",
            "不需要",
            "不要",
            "否",
            "no",
            "n",
            "拒绝",
            "不同意",
        ]

        user_response_lower = user_response.lower()

        # 检查确认关键词
        for keyword in confirm_keywords:
            if keyword in user_response_lower:
                return True

        # 检查拒绝关键词
        for keyword in reject_keywords:
            if keyword in user_response_lower:
                return False

        # 如果不明确，返回None
        return None

    def _generate_confirmation_prompt(self, detection_result: Dict[str, Any]) -> str:
        """
        生成确认提示

        Args:
            detection_result: 检测结果

        Returns:
            确认提示文本
        """
        # 提取检测信息
        detections = detection_result.get("detections", [])
        disease_count = len(detections)

        if disease_count == 0:
            disease_info = "未检测到病害"
        elif disease_count == 1:
            disease_name = detections[0].get("name", "未知病害")
            confidence = detections[0].get("confidence", 0)
            disease_info = f"检测到 {disease_name} (置信度: {confidence:.1%})"
        else:
            disease_names = [
                det.get("name", "未知") for det in detections[:3]
            ]  # 最多显示3个
            disease_info = f"检测到 {disease_count} 种病害: {', '.join(disease_names)}"

        # 生成确认提示
        confirmation_prompt = (
            f"检测已完成！\n\n"
            f"[CHART] **检测结果**: {disease_info}\n\n"
            f"[DETECT] **请选择您想了解的内容（回复 1、2 或 3）**:\n"
            f"1. **防治方案** - 针对检测到的病害\n"
            f"2. **种植规划** - 适合的种植建议\n"
            f"3. **灌溉策略** - 优化的灌溉方案\n"
        )

        return confirmation_prompt

    def _should_skip_confirmation(self, detection_result: Dict[str, Any]) -> bool:
        """
        判断是否应该跳过确认

        Args:
            detection_result: 检测结果

        Returns:
            True - 跳过确认, False - 需要确认
        """
        # 1. 如果没有检测到病害，跳过确认
        detections = detection_result.get("detections", [])
        if len(detections) == 0:
            logger.info("未检测到病害，跳过确认")
            return True

        # 2. 如果用户明确要求查询相关知识，自动确认
        user_input = self._get_user_response().lower()
        query_keywords = [
            "防治",
            "治疗",
            "预防",
            "种植",
            "灌溉",
            "方案",
            "建议",
            "策略",
        ]
        for keyword in query_keywords:
            if keyword in user_input:
                logger.info(f"用户输入包含关键词 '{keyword}'，自动确认查询相关知识")
                self.memory.metadata["user_confirmed"] = True
                return True

        # 3. 如果意图是查询相关知识的，自动确认
        intent = self.memory.metadata.get("intent", "")
        if intent in ["prevention", "planting", "irrigation", "query"]:
            logger.info(f"意图为 '{intent}'，自动确认查询相关知识")
            self.memory.metadata["user_confirmed"] = True
            return True

        # 4. 如果用户之前已经确认过，跳过确认
        if self.memory.metadata.get("user_confirmed") is True:
            logger.info("用户已确认过，跳过确认")
            return True

        # 5. 默认需要确认
        logger.info("需要用户确认是否查询相关知识")
        return False


def create_confirmation_agent(memory: Memory, **kwargs) -> ConfirmationAgent:
    """
    创建确认Agent

    Args:
        memory: 记忆实例
        **kwargs: 额外参数

    Returns:
        ConfirmationAgent实例
    """
    return ConfirmationAgent(memory=memory, **kwargs)
