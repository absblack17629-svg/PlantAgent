# -*- coding: utf-8 -*-
"""
Skill 系统初始化模块
"""

from .base_skill import BaseSkill
from .skill_registry import SkillRegistry, get_skill_registry
from .detection_skill import DetectionSkill
from .knowledge_skill import KnowledgeSkill
from .memory_skill import MemorySkill
from .planting_plan_skill import PlantingPlanSkill
from .weather_skill import WeatherSkill
from .irrigation_skill import IrrigationSkill

__all__ = [
    'BaseSkill',
    'SkillRegistry',
    'get_skill_registry',
    'DetectionSkill',
    'KnowledgeSkill',
    'MemorySkill',
    'PlantingPlanSkill',
    'WeatherSkill',
    'IrrigationSkill',
]
