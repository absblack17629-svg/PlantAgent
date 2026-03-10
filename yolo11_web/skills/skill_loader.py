# -*- coding: utf-8 -*-
"""
Skill 加载器 - 从 Markdown 文档加载 Skill 定义

设计理念：
- Skill 的实现代码不写死在 Python 中
- 而是用自然语言在 Markdown 中描述
- LLM 阅读文档后自行生成调用代码
- 类似 Claude Code / Cursor 的 tool 定义方式
"""

import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class SkillDefinition:
    """Skill 定义 - 从 Markdown 文档解析"""
    
    def __init__(self, name: str, markdown_content: str, file_path: str):
        self.name = name
        self.markdown = markdown_content
        self.file_path = file_path
        self._parse()
    
    def _parse(self):
        """解析 Markdown 文档，提取各部分内容"""
        lines = self.markdown.split('\n')
        
        # 提取标题（Skill 名称）
        self.title = ""
        self.description = ""
        
        # 提取各个部分
        self.params: Dict[str, Dict] = {}
        self.return_format = ""
        self.examples: List[str] = []
        self.notes: List[str] = []
        
        current_section = ""
        current_content = []
        
        for line in lines:
            line = line.rstrip()
            
            # 检测章节标题
            if line.startswith('# '):
                self.title = line[2:].strip()
                continue
            elif line.startswith('## '):
                # 保存之前的内容
                self._save_section(current_section, current_content)
                current_section = line[3:].strip()
                current_content = []
                continue
            
            current_content.append(line)
        
        # 保存最后一节
        self._save_section(current_section, current_content)
    
    def _save_section(self, section: str, content: List[str]):
        """保存解析的章节内容"""
        if not section or not content:
            return
        
        text = '\n'.join(content).strip()
        
        if section == "描述":
            self.description = text
        elif section == "参数":
            self._parse_params(text)
        elif section == "返回值格式":
            self.return_format = text
        elif section == "使用示例":
            self.examples.append(text)
        elif section == "注意事项":
            self.notes = [line.strip() for line in text.split('\n') if line.strip()]
    
    def _parse_params(self, text: str):
        """解析参数定义"""
        # 匹配 "- `param_name` (必填/可选): 描述" 格式
        pattern = r'- `(\w+)` \(([^)]+)\): (.+)'
        
        for match in re.finditer(pattern, text):
            param_name = match.group(1)
            required = match.group(2)
            desc = match.group(3)
            
            self.params[param_name] = {
                "name": param_name,
                "required": "必填" in required,
                "description": desc.strip(),
                "optional_values": self._extract_enum_values(desc)
            }
    
    def _extract_enum_values(self, text: str) -> Optional[List[str]]:
        """提取可选值"""
        # 匹配 "可选值: a, b, c" 格式
        match = re.search(r'可选值[:：]\s*(.+)', text)
        if match:
            values = match.group(1).split(',')
            return [v.strip() for v in values]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，供 LLM 使用"""
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "params": self.params,
            "return_format": self.return_format,
            "examples": self.examples,
            "notes": self.notes,
            "markdown": self.markdown,  # 完整文档，让 LLM 理解
        }
    
    def to_langchain_tool(self):
        """
        转换为 LangChain @tool 格式
        注意：这个只是格式转换，实际执行由 LLM 决定
        """
        from langchain_core.tools import tool
        
        # 构建工具的描述文本
        desc = f"{self.title}\n\n{self.description}\n\n参数:\n"
        for param_name, param_info in self.params.items():
            required_str = "必填" if param_info["required"] else "可选"
            desc += f"- {param_name} ({required_str}): {param_info['description']}\n"
        
        # 添加返回格式说明
        desc += f"\n返回: {self.return_format[:200]}..." if len(self.return_format) > 200 else f"\n返回: {self.return_format}"
        
        @tool(self.name, description=desc)
        async def dynamic_tool(**kwargs) -> str:
            """
            动态工具 - 由 LLM 根据 Skill 文档描述自行决定实现
            
            注意：这个函数本身不包含具体实现
            LLM 会阅读 Skill 文档后生成调用代码
            """
            # 返回文档信息，让调用者（LLM）决定如何执行
            return {
                "skill": self.name,
                "document": self.markdown,
                "params": kwargs,
                "message": "此工具需要由 LLM 根据 Skill 文档描述自行执行"
            }
        
        return dynamic_tool


class SkillLoader:
    """Skill 加载器 - 从指定目录加载 Markdown 文件"""
    
    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            # 默认使用 skills_md 目录
            base_dir = Path(__file__).parent
            skills_dir = base_dir / "skills_md"
        
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, SkillDefinition] = {}
    
    def load_all(self) -> Dict[str, SkillDefinition]:
        """加载所有 Markdown 文件"""
        if not self.skills_dir.exists():
            print(f"[WARN] Skills directory not found: {self.skills_dir}")
            return {}
        
        for md_file in self.skills_dir.glob("*.md"):
            skill_name = md_file.stem  # 文件名（不含扩展名）
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                skill = SkillDefinition(skill_name, content, str(md_file))
                self.skills[skill_name] = skill
                print(f"[OK] Loaded Skill: {skill_name}")
                
            except Exception as e:
                print(f"[FAIL] Load Skill failed {md_file.name}: {e}")
        
        return self.skills
    
    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """获取指定 Skill"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有 Skills"""
        return [
            {
                "name": name,
                "title": skill.title,
                "description": skill.description[:100] + "..." if len(skill.description) > 100 else skill.description,
                "params_count": len(skill.params),
            }
            for name, skill in self.skills.items()
        ]
    
    def get_all_markdown(self) -> List[Dict[str, str]]:
        """获取所有 Skill 的 Markdown 文档"""
        return [
            {
                "name": name,
                "content": skill.markdown
            }
            for name, skill in self.skills.items()
        ]


# 全局单例
_skill_loader: Optional[SkillLoader] = None


def get_skill_loader() -> SkillLoader:
    """获取 Skill 加载器单例"""
    global _skill_loader
    if _skill_loader is None:
        _skill_loader = SkillLoader()
        _skill_loader.load_all()
    return _skill_loader


def reload_skills() -> SkillLoader:
    """重新加载所有 Skills"""
    global _skill_loader
    _skill_loader = SkillLoader()
    _skill_loader.load_all()
    return _skill_loader