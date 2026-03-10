# -*- coding: utf-8 -*-
"""
Skill 系统初始化模块

新架构：声明式 Skill
- Skill 定义在 Markdown 文档中（skills/skills_md/*.md）
- 包含自然语言描述的参数、返回值、示例
- LLM 阅读文档后自行生成调用代码
- 不需要预先编写 Python 实现代码

使用方式：
    from skills import get_skill_loader
    
    loader = get_skill_loader()
    skills = loader.list_skills()  # 获取所有技能列表
    skill = loader.get_skill("detection")  # 获取单个技能
    docs = loader.get_all_markdown()  # 获取所有技能文档
"""

# 导入新的 SkillLoader
from .skill_loader import (
    SkillLoader,
    SkillDefinition,
    get_skill_loader,
    reload_skills,
)

# 导出
__all__ = [
    'SkillLoader',
    'SkillDefinition', 
    'get_skill_loader',
    'reload_skills',
]

# 自动加载
print("[Skill] Initializing declarative skill system...")
_loader = get_skill_loader()
print(f"[Skill] Loaded {_loader.skills} skills")