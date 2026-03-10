# -*- coding: utf-8 -*-
"""
基础技能类 - 所有技能的抽象基类

[WARN] 废弃警告 (DEPRECATED)
==========================================
本文件已被新架构取代，将在 2026-07 后移除。

新架构路径：
- services/tools/base.py

迁移指南：.kiro/specs/architecture-refactoring/migration-guide.md
==========================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseSkill(ABC):
    """技能基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "未提供描述"
        self.enabled = True
        logger.info(f"[OK] 技能初始化: {self.name}")
    
    @abstractmethod
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        获取技能提供的能力列表
        
        Returns:
            能力列表，每个能力包含：
            - name: 能力名称
            - description: 能力描述
            - parameters: 参数定义
        """
        pass
    
    @abstractmethod
    async def execute(self, capability_name: str, **kwargs) -> Any:
        """
        执行指定的能力
        
        Args:
            capability_name: 能力名称
            **kwargs: 能力参数
        
        Returns:
            执行结果
        """
        pass
    
    def enable(self):
        """启用技能"""
        self.enabled = True
        logger.info(f"[OK] 技能已启用: {self.name}")
    
    def disable(self):
        """禁用技能"""
        self.enabled = False
        logger.info(f"[WARN] 技能已禁用: {self.name}")
    
    def is_enabled(self) -> bool:
        """检查技能是否启用"""
        return self.enabled
    
    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "capabilities": self.get_capabilities()
        }
