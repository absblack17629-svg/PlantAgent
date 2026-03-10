# -*- coding: utf-8 -*-
"""
Token 计数器

用于估算 LLM 请求的 token 数量。
"""

from typing import List, Dict, Any


class TokenCounter:
    """Token 计数器"""
    
    # Token 常量
    BASE_MESSAGE_TOKENS = 4  # 每条消息的基础 token
    TOKENS_PER_NAME = 1      # 名称字段的 token
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """初始化 Token 计数器
        
        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
    
    def count_text(self, text: str) -> int:
        """估算文本的 token 数量
        
        简单估算：中文约 1.5 字符/token，英文约 4 字符/token
        
        Args:
            text: 文本内容
            
        Returns:
            估算的 token 数量
        """
        if not text:
            return 0
        
        # 统计中英文字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        
        # 估算 token 数
        tokens = int(chinese_chars / 1.5 + other_chars / 4)
        return max(tokens, 1)
    
    def count_messages(self, messages: List[Dict[str, Any]]) -> int:
        """估算消息列表的 token 数量
        
        Args:
            messages: 消息列表
            
        Returns:
            估算的 token 数量
        """
        total_tokens = 0
        
        for message in messages:
            # 基础 token
            total_tokens += self.BASE_MESSAGE_TOKENS
            
            # 角色名称
            if "role" in message:
                total_tokens += self.TOKENS_PER_NAME
            
            # 内容
            if "content" in message:
                content = message["content"]
                if isinstance(content, str):
                    total_tokens += self.count_text(content)
                elif isinstance(content, list):
                    # 多模态内容
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            total_tokens += self.count_text(item["text"])
            
            # 名称字段
            if "name" in message:
                total_tokens += self.TOKENS_PER_NAME
        
        return total_tokens
    
    def check_limit(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int,
        reserve_tokens: int = 500
    ) -> tuple[bool, int]:
        """检查消息是否超过 token 限制
        
        Args:
            messages: 消息列表
            max_tokens: 最大 token 数
            reserve_tokens: 预留 token 数（用于响应）
            
        Returns:
            (是否在限制内, 当前 token 数)
        """
        current_tokens = self.count_messages(messages)
        is_within_limit = (current_tokens + reserve_tokens) <= max_tokens
        return is_within_limit, current_tokens
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "model_name": self.model_name,
            "base_message_tokens": self.BASE_MESSAGE_TOKENS,
            "tokens_per_name": self.TOKENS_PER_NAME,
        }


__all__ = ["TokenCounter"]
