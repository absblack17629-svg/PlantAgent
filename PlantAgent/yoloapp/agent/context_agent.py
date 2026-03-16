# -*- coding: utf-8 -*-
"""
ContextAgent - 上下文管理 Agent

实现功能：
1. 对话压缩：每轮对话后压缩历史，只保留关键信息
2. 分层记忆：近10轮对话为短期记忆，超过10轮为长期记忆（摘要形式）
3. 增量更新：只更新新对话，筛选冗余重复信息去除
"""

from typing import List, Dict, Any, Optional
from pydantic import Field
import hashlib
import re

from yoloapp.agent.base import BaseAgent
from yoloapp.schema import AgentRole, AgentState, Message, Memory
from yoloapp.prompt.context_prompts import (
    CONTEXT_SYSTEM_PROMPT,
    CONTEXT_COMPRESSION_TEMPLATE,
    CONTEXT_PREFERENCE_ANALYSIS_TEMPLATE,
)
from yoloapp.utils.logger import get_logger
from yoloapp.llm import get_llm_client

logger = get_logger(__name__)


class ContextSummary:
    """对话摘要结构"""

    def __init__(
        self,
        summary: str = "",
        key_entities: List[str] = None,
        user_intent_evolution: str = "",
        completed_actions: List[str] = None,
        pending_issues: List[str] = None,
        focus_points: List[str] = None,
        turn_count: int = 0,
    ):
        self.summary = summary
        self.key_entities = key_entities or []
        self.user_intent_evolution = user_intent_evolution
        self.completed_actions = completed_actions or []
        self.pending_issues = pending_issues or []
        self.focus_points = focus_points or []
        self.turn_count = turn_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "key_entities": self.key_entities,
            "user_intent_evolution": self.user_intent_evolution,
            "completed_actions": self.completed_actions,
            "pending_issues": self.pending_issues,
            "focus_points": self.focus_points,
            "turn_count": self.turn_count,
        }

    def to_prompt(self) -> str:
        """转换为提示词格式"""
        lines = [f"【对话摘要】共 {self.turn_count} 轮对话"]
        if self.summary:
            lines.append(f"概要: {self.summary}")
        if self.key_entities:
            lines.append(f"关键实体: {', '.join(self.key_entities)}")
        if self.completed_actions:
            lines.append(f"已完成: {', '.join(self.completed_actions)}")
        if self.pending_issues:
            lines.append(f"待解决: {', '.join(self.pending_issues)}")
        if self.focus_points:
            lines.append(f"关注点: {', '.join(self.focus_points)}")
        return "\n".join(lines)


class ContextAgent(BaseAgent):
    """
    上下文管理 Agent

    功能：
    1. 对话历史压缩：每轮对话后压缩，保留关键信息
    2. 分层记忆：
       - 短期记忆：近10轮对话完整保留
       - 长期记忆：超过10轮的对话摘要
    3. 增量更新：只更新新对话，去除冗余重复信息
    """

    # 配置参数
    short_term_turns: int = Field(default=10, description="短期记忆保留轮数")
    compression_threshold: int = Field(default=3, description="触发压缩的对话轮数")
    max_summary_length: int = Field(default=200, description="摘要最大长度")
    deduplication_similarity: float = Field(default=0.85, description="去重相似度阈值")

    # 内部状态（使用 Pydantic 兼容的名称）
    long_term_summary_data: Optional[Dict[str, Any]] = Field(
        default=None, description="长期记忆摘要数据"
    )
    message_hashes: List[str] = Field(default_factory=list, description="消息哈希列表")
    last_update_turn: int = Field(default=0, description="上次更新的轮数")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, skill_client=None, **data):
        if "name" not in data:
            data["name"] = "ContextAgent"
        if "role" not in data:
            data["role"] = AgentRole.CONTEXT_MANAGER
        super().__init__(**data)
        self.skill_client = skill_client
        self.description = "上下文管理 - 对话压缩 + 分层记忆 + 增量更新"
        self._llm_client = None
        self._long_term_summary_cache = None

    @property
    def _long_term_summary(self) -> Optional[ContextSummary]:
        """获取长期记忆摘要（缓存）"""
        return self._long_term_summary_cache

    @_long_term_summary.setter
    def _long_term_summary(self, value: Optional[ContextSummary]):
        """设置长期记忆摘要"""
        self._long_term_summary_cache = value
        if value:
            self.long_term_summary_data = value.to_dict()
        else:
            self.long_term_summary_data = None

    def _get_llm_client(self):
        """获取 LLM 客户端"""
        if self._llm_client is None:
            try:
                self._llm_client = get_llm_client()
            except Exception as e:
                logger.warning(f"获取 LLM 客户端失败: {e}")
        return self._llm_client

    def _compute_hash(self, content: str) -> str:
        """计算消息内容的哈希值"""
        return hashlib.md5(content.encode("utf-8")).hexdigest()[:16]

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（简单实现）"""
        if not text1 or not text2:
            return 0.0

        text1_set = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", text1.lower()))
        text2_set = set(re.findall(r"[\u4e00-\u9fa5a-zA-Z0-9]+", text2.lower()))

        if not text1_set or not text2_set:
            return 0.0

        intersection = len(text1_set & text2_set)
        union = len(text1_set | text2_set)

        return intersection / union if union > 0 else 0.0

    def _is_duplicate(self, message: Message) -> bool:
        """检查消息是否与历史消息重复"""
        content = message.content or ""
        current_hash = self._compute_hash(content)

        if current_hash in self.message_hashes:
            return True

        for old_hash in self.message_hashes[-5:]:
            old_msg = None
            for msg in self.memory.messages:
                if self._compute_hash(msg.content or "") == old_hash:
                    old_msg = msg
                    break

            if (
                old_msg
                and self._compute_similarity(content, old_msg.content or "")
                > self.deduplication_similarity
            ):
                logger.info(f"[ContextAgent] 检测到相似消息，标记为重复")
                return True

        return False

    def _filter_duplicates(self, messages: List[Message]) -> List[Message]:
        """过滤重复消息"""
        filtered = []
        for msg in messages:
            if not self._is_duplicate(msg):
                filtered.append(msg)
                self.message_hashes.append(self._compute_hash(msg.content or ""))

        return filtered

    def _get_conversation_turns(self) -> int:
        """获取当前对话轮数（用户-助手交互对）"""
        turns = 0
        for msg in self.memory.messages:
            if msg.role == "assistant":
                turns += 1
        return turns

    async def _compress_conversation(
        self, recent_messages: List[Message]
    ) -> ContextSummary:
        """使用 LLM 压缩对话"""
        client = self._get_llm_client()

        if not client:
            logger.warning("[ContextAgent] 无法获取 LLM，使用简单压缩")
            return self._simple_compress(recent_messages)

        history_text = "\n".join(
            [
                f"{msg.role}: {msg.content[:100]}"
                for msg in recent_messages[-self.compression_threshold * 2 :]
            ]
        )

        prompt = CONTEXT_COMPRESSION_TEMPLATE.format(
            turn_count=len(recent_messages) // 2,
            history=history_text,
            current_request=recent_messages[-1].content if recent_messages else "",
        )

        try:
            response = await client.ask(
                [
                    Message.system_message(CONTEXT_SYSTEM_PROMPT),
                    Message.user_message(prompt),
                ]
            )

            import json

            try:
                result = json.loads(response)
                return ContextSummary(
                    summary=result.get("summary", "")[: self.max_summary_length],
                    key_entities=result.get("key_entities", []),
                    user_intent_evolution=result.get("user_intent_evolution", ""),
                    completed_actions=result.get("completed_actions", []),
                    pending_issues=result.get("pending_issues", []),
                    focus_points=result.get("focus_points", []),
                    turn_count=len(recent_messages) // 2,
                )
            except json.JSONDecodeError:
                logger.warning("[ContextAgent] LLM 返回非 JSON，使用简单压缩")
                return self._simple_compress(recent_messages)

        except Exception as e:
            logger.warning(f"[ContextAgent] LLM 调用失败: {e}，使用简单压缩")
            return self._simple_compress(recent_messages)

    def _simple_compress(self, messages: List[Message]) -> ContextSummary:
        """简单的压缩方法（无 LLM 时使用）"""
        from config.settings import settings
        
        user_messages = [m.content for m in messages if m.role == "user"]
        assistant_messages = [m.content for m in messages if m.role == "assistant"]

        entities = []
        pattern = settings.agricultural_entities_pattern
        for msg in user_messages + assistant_messages:
            found = re.findall(f"({pattern})", msg)
            entities.extend(found)

        return ContextSummary(
            summary=f"对话记录，共 {len(messages) // 2} 轮",
            key_entities=list(set(entities)),
            completed_actions=[],
            pending_issues=[],
            turn_count=len(messages) // 2,
        )

    def _build_context_prompt(self) -> str:
        """构建上下文提示词"""
        parts = []

        if self._long_term_summary and self._long_term_summary.turn_count > 0:
            parts.append("【长期记忆】")
            parts.append(self._long_term_summary.to_prompt())

        recent_count = min(self.short_term_turns, len(self.memory.messages))
        recent_msgs = self.memory.messages[-recent_count:] if recent_count > 0 else []

        if recent_msgs:
            parts.append("\n【近期对话】（最近 {} 轮）".format(recent_count // 2))
            for msg in recent_msgs:
                role_label = "用户" if msg.role == "user" else "助手"
                content = (
                    msg.content[:150] + "..."
                    if len(msg.content or "") > 150
                    else msg.content
                )
                parts.append(f"{role_label}: {content}")

        return "\n".join(parts)

    async def step(self) -> str:
        """
        执行上下文管理步骤

        流程：
        1. 检查是否需要增量更新
        2. 过滤重复消息
        3. 判断是否需要压缩
        4. 执行压缩并更新长期记忆
        5. 构建上下文提示词
        """
        self.state = AgentState.RUNNING

        current_turns = self._get_conversation_turns()
        logger.info(f"[ContextAgent] 当前对话轮数: {current_turns}")

        if current_turns <= self.last_update_turn:
            logger.info("[ContextAgent] 无新对话，跳过更新")
            self.state = AgentState.FINISHED
            return "无新对话需要处理"

        new_turns = current_turns - self.last_update_turn
        logger.info(f"[ContextAgent] 新增 {new_turns} 轮对话，执行增量更新")

        new_messages = self.memory.messages[-new_turns * 2 :]

        filtered_messages = self._filter_duplicates(new_messages)

        total_turns = self._get_conversation_turns()

        if total_turns >= self.compression_threshold:
            logger.info(
                f"[ContextAgent] 对话轮数 {total_turns} >= {self.compression_threshold}，执行压缩"
            )

            all_recent = (
                self.memory.messages[-self.short_term_turns * 2 :]
                if self.short_term_turns > 0
                else []
            )
            summary = await self._compress_conversation(all_recent)

            if self._long_term_summary:
                self._long_term_summary.summary += " | " + summary.summary
                self._long_term_summary.turn_count += summary.turn_count
                self._long_term_summary.key_entities = list(
                    set(self._long_term_summary.key_entities + summary.key_entities)
                )
                self._long_term_summary.completed_actions = list(
                    set(
                        self._long_term_summary.completed_actions
                        + summary.completed_actions
                    )
                )
            else:
                self._long_term_summary = summary

            logger.info(f"[ContextAgent] 压缩完成，摘要: {summary.summary[:50]}...")
        else:
            logger.info(
                f"[ContextAgent] 对话轮数 {total_turns} < {self.compression_threshold}，跳过压缩"
            )

        self.last_update_turn = current_turns

        context_prompt = self._build_context_prompt()
        self.memory.metadata["context_prompt"] = context_prompt
        self.memory.metadata["long_term_summary"] = (
            self._long_term_summary.to_dict() if self._long_term_summary else {}
        )
        self.memory.metadata["short_term_turns"] = min(
            self.short_term_turns, total_turns
        )

        logger.info(
            f"[ContextAgent] 上下文构建完成，短期记忆 {min(self.short_term_turns, total_turns)} 轮"
        )

        self.state = AgentState.FINISHED
        return "上下文管理完成"

    def get_context_for_prompt(self) -> str:
        """获取用于 LLM 提示词的上下文"""
        return self.memory.metadata.get("context_prompt", "")

    def get_long_term_summary(self) -> Optional[Dict[str, Any]]:
        """获取长期记忆摘要"""
        return self.memory.metadata.get("long_term_summary", {})

    def clear_history(self):
        """清除历史记录"""
        self.memory.messages.clear()
        self._long_term_summary = None
        self._message_hashes.clear()
        self.last_update_turn = 0
        logger.info("[ContextAgent] 历史记录已清除")
