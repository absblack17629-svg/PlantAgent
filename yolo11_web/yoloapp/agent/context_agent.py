# -*- coding: utf-8 -*-
"""
节点2: 上下文管理 Agent
负责加载和整合上下文信息
"""

from typing import Dict, List, Optional
from .base import BaseAgent
from yoloapp.schema import AgentRole, AgentState as SchemaAgentState, Message, Memory
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class ContextAgent(BaseAgent):
    """
    上下文管理 Agent
    
    职责:
    - 加载图片上下文
    - 加载历史对话记忆
    - 整合意图上下文
    - 构建完整的上下文信息
    """
    
    def __init__(self, skill_client=None):
        super().__init__(
            name="ContextAgent",
            role=AgentRole.CONTEXT_MANAGER,
            description="负责加载和整合上下文信息"
        )
        self.skill_client = skill_client
    
    async def step(self) -> str:
        """
        执行上下文管理步骤
        
        Returns:
            上下文信息字符串
        """
        try:
            logger.info(f"[{self.name}] 开始加载上下文...")
            
            context_parts = []
            
            # 1. 从 Memory 中获取用户输入和图片路径
            user_input = self._get_user_input()
            image_path = self._get_image_path()
            intent = self._get_intent()
            
            # 2. 加载图片上下文
            if image_path:
                context_parts.append(f"[图片路径: {image_path}]")
                logger.debug(f"[{self.name}] 加载图片上下文: {image_path}")
            
            # 3. 加载历史记忆上下文
            if self.skill_client:
                try:
                    history = await self._load_history()
                    if history and "暂无" not in history:
                        context_parts.append(f"[历史记录]\n{history}")
                        logger.debug(f"[{self.name}] 加载历史记忆: {len(history)} 字符")
                except Exception as e:
                    logger.warning(f"[{self.name}] 加载历史记忆失败: {e}")
            
            # 4. 加载意图上下文
            if intent:
                context_parts.append(f"[用户意图: {intent}]")
                logger.debug(f"[{self.name}] 加载意图上下文: {intent}")
            
            # 5. 组合上下文
            context = "\n\n".join(context_parts) if context_parts else ""
            
            # 6. 保存到 Memory
            self.memory.add_message(Message(
                role="system",
                content=f"上下文信息已加载: {len(context)} 字符"
            ))
            
            # 7. 存储上下文到 metadata
            self.memory.metadata["context"] = context
            
            logger.info(f"[{self.name}] 上下文加载完成: {len(context)} 字符")
            
            return context
            
        except Exception as e:
            error_msg = f"上下文加载失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    def _get_user_input(self) -> str:
        """从 Memory 中获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""
    
    def _get_image_path(self) -> Optional[str]:
        """从 Memory metadata 中获取图片路径"""
        return self.memory.metadata.get("image_path")
    
    def _get_intent(self) -> Optional[str]:
        """从 Memory metadata 中获取意图"""
        return self.memory.metadata.get("intent")
    
    async def _load_history(self) -> str:
        """加载历史记忆"""
        if not self.skill_client:
            return ""
        
        try:
            history = await self.skill_client.call_capability(
                "MemorySkill", 
                "get_task_history", 
                limit=3
            )
            return str(history) if history else ""
        except Exception as e:
            logger.warning(f"[{self.name}] 加载历史失败: {e}")
            return ""
