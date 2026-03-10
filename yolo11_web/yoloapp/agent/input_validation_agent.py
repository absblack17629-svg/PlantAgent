# -*- coding: utf-8 -*-
"""
节点5: 输入验证 Agent
负责检查用户输入的完整性
"""

from typing import Dict, List
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class InputValidationAgent(BaseAgent):
    """
    输入验证 Agent
    
    职责:
    - 检查用户输入完整性
    - 识别缺失信息
    - 生成澄清请求
    """
    
    def __init__(self):
        super().__init__(
            name="InputValidationAgent",
            role=AgentRole.VALIDATOR,
            description="负责检查用户输入的完整性"
        )
    
    async def step(self) -> str:
        """
        执行输入验证步骤
        
        Returns:
            验证结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始验证输入...")
            
            # 1. 获取必要信息
            intent = self.memory.metadata.get("intent", "chat")
            user_input = self._get_user_input()
            image_path = self.memory.metadata.get("image_path")
            
            # 2. 执行验证
            validation = self._validate_input(intent, user_input, image_path)
            
            # 3. 保存验证结果到 metadata
            self.memory.metadata["input_validation"] = validation
            
            # 4. 记录到 Memory
            if validation["is_complete"]:
                result = "[OK] 输入验证通过：所有必要信息已提供"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
            else:
                missing = ", ".join(validation["missing_info"])
                result = f"[WARN] 输入不完整，缺少: {missing}"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
            
            logger.info(f"[{self.name}] 验证完成: is_complete={validation['is_complete']}")
            
            return result
            
        except Exception as e:
            error_msg = f"输入验证失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise AgentError(error_msg, agent_name=self.name)
    
    def _get_user_input(self) -> str:
        """从 Memory 中获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""
    
    def _validate_input(self, intent: str, user_input: str, image_path: str) -> Dict:
        """
        验证用户输入完整性
        
        Args:
            intent: 用户意图
            user_input: 用户输入文本
            image_path: 图片路径
            
        Returns:
            验证结果字典
        """
        validation = {
            "is_complete": True,
            "missing_info": [],
            "clarification_needed": False,
            "clarification_prompt": ""
        }
        
        # 检测意图需要图片
        if intent == "detect":
            if not image_path:
                validation["is_complete"] = False
                validation["missing_info"].append("图片")
                validation["clarification_needed"] = True
                validation["clarification_prompt"] = "您想要进行病害检测，请问可以提供一张需要检测的图片吗？"
        
        # 查询意图检查问题是否明确
        elif intent == "query":
            if not user_input or len(user_input.strip()) < 2:
                validation["is_complete"] = False
                validation["missing_info"].append("问题描述")
                validation["clarification_needed"] = True
                validation["clarification_prompt"] = "您的问题描述不够清晰，请补充更多细节，例如：水稻叶子上出现了什么症状？"
        
        # 普通对话意图检查
        elif intent == "chat":
            if not user_input or len(user_input.strip()) < 1:
                validation["is_complete"] = False
                validation["missing_info"].append("对话内容")
                validation["clarification_needed"] = True
                validation["clarification_prompt"] = "您好，请问有什么可以帮助您的？"
        
        # 问候和告别不需要验证
        elif intent in ["greet", "goodbye"]:
            validation["is_complete"] = True
        
        return validation
