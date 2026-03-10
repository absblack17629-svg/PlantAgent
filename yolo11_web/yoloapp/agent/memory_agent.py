# -*- coding: utf-8 -*-
"""
节点3: 对话记忆 Agent
负责保存和检索对话记忆
"""

from typing import Dict, Optional
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryAgent(BaseAgent):
    """
    对话记忆 Agent
    
    职责:
    - 保存当前对话到记忆系统
    - 构建记忆内容
    - 调用 MemorySkill 持久化
    """
    
    def __init__(self, skill_client=None):
        super().__init__(
            name="MemoryAgent",
            role=AgentRole.MEMORY_MANAGER,
            description="负责保存和检索对话记忆"
        )
        self.skill_client = skill_client
    
    async def step(self) -> str:
        """
        执行记忆保存步骤
        
        Returns:
            保存结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始保存记忆...")
            
            # 1. 检查是否有 skill_client
            if not self.skill_client:
                logger.warning(f"[{self.name}] 无可用的 MemorySkill，跳过保存")
                return "记忆保存跳过（无可用的MemorySkill）"
            
            # 2. 构建记忆内容
            memory_content = self._build_memory_content()
            
            # 3. 保存到 MemorySkill
            success = await self._save_to_skill(memory_content)
            
            # 4. 记录结果
            if success:
                result = "记忆保存成功"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
                logger.info(f"[{self.name}] {result}")
            else:
                result = "记忆保存失败"
                logger.warning(f"[{self.name}] {result}")
            
            return result
            
        except Exception as e:
            error_msg = f"记忆保存失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    def _build_memory_content(self) -> str:
        """构建记忆内容"""
        parts = []
        
        # 1. 用户输入
        user_input = self._get_user_input()
        if user_input:
            parts.append(f"用户: {user_input}")
        
        # 2. 意图
        intent = self.memory.metadata.get("intent")
        if intent:
            parts.append(f"意图: {intent}")
        
        # 3. 上下文（截取前200字符）
        context = self.memory.metadata.get("context", "")
        if context:
            context_preview = context[:200] + "..." if len(context) > 200 else context
            parts.append(f"上下文: {context_preview}")
        
        return "\n".join(parts)
    
    def _get_user_input(self) -> str:
        """从 Memory 中获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""
    
    async def _save_to_skill(self, content: str) -> bool:
        """保存到 MemorySkill"""
        try:
            await self.skill_client.call_capability(
                "MemorySkill",
                "save_context",
                context=content,
                context_type="conversation"
            )
            return True
        except Exception as e:
            logger.error(f"[{self.name}] 保存到 MemorySkill 失败: {e}")
            return False
