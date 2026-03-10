# -*- coding: utf-8 -*-
"""
技能注册中心 - 管理所有技能的注册和调用
"""

from typing import Dict, List, Any, Optional
from .base_skill import BaseSkill
from utils.logger import get_logger

logger = get_logger(__name__)


class SkillRegistry:
    """技能注册中心"""
    
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        logger.info("[OK] 技能注册中心初始化")
    
    def register(self, skill: BaseSkill):
        """
        注册技能
        
        Args:
            skill: 技能实例
        """
        skill_name = skill.name
        if skill_name in self.skills:
            logger.warning(f"[WARN] 技能 {skill_name} 已存在，将被覆盖")
        
        self.skills[skill_name] = skill
        logger.info(f"[OK] 技能已注册: {skill_name}")
    
    def unregister(self, skill_name: str) -> bool:
        """
        注销技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            是否成功
        """
        if skill_name in self.skills:
            del self.skills[skill_name]
            logger.info(f"[OK] 技能已注销: {skill_name}")
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取技能实例
        
        Args:
            skill_name: 技能名称
        
        Returns:
            技能实例或None
        """
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """
        列出所有技能
        
        Returns:
            技能信息列表
        """
        return [skill.get_info() for skill in self.skills.values()]
    
    def get_all_capabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取所有技能的能力
        
        Returns:
            字典，key为技能名称，value为能力列表
        """
        capabilities_map = {}
        for skill_name, skill in self.skills.items():
            if skill.is_enabled():
                capabilities_map[skill_name] = skill.get_capabilities()
        return capabilities_map
    
    async def execute_capability(self, skill_name: str, capability_name: str, **kwargs) -> Any:
        """
        执行技能能力
        
        Args:
            skill_name: 技能名称
            capability_name: 能力名称
            **kwargs: 能力参数
        
        Returns:
            执行结果
        """
        skill = self.get_skill(skill_name)
        
        if not skill:
            error_msg = f"技能 '{skill_name}' 不存在"
            logger.error(error_msg)
            return error_msg
        
        if not skill.is_enabled():
            error_msg = f"技能 '{skill_name}' 已禁用"
            logger.error(error_msg)
            return error_msg
        
        try:
            result = await skill.execute(capability_name, **kwargs)
            logger.info(f"[OK] 能力执行成功: {skill_name}.{capability_name}")
            return result
        except Exception as e:
            error_msg = f"能力执行失败 {skill_name}.{capability_name}: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return error_msg


# 全局单例
_skill_registry_instance = None


def get_skill_registry() -> SkillRegistry:
    """获取技能注册中心单例"""
    global _skill_registry_instance
    if _skill_registry_instance is None:
        _skill_registry_instance = SkillRegistry()
    return _skill_registry_instance
