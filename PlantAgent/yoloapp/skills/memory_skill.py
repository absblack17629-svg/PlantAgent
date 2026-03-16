# -*- coding: utf-8 -*-
"""
记忆管理技能
提供任务管理、上下文保存和记忆搜索能力
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from .base_skill import BaseSkill


# 持久化存储路径
MEMORY_STORAGE_DIR = "./memory_storage"
TASK_NOTES_FILE = os.path.join(MEMORY_STORAGE_DIR, "task_notes.json")
CONTEXT_HISTORY_FILE = os.path.join(MEMORY_STORAGE_DIR, "context_history.json")


class MemoryManager:
    """记忆管理器（支持持久化）"""
    
    def __init__(self):
        self.task_notes = []
        self.context_history = []
        self.current_task = None
        
        os.makedirs(MEMORY_STORAGE_DIR, exist_ok=True)
        self._load_from_disk()
    
    def _load_from_disk(self):
        """从磁盘加载持久化数据"""
        try:
            if os.path.exists(TASK_NOTES_FILE):
                with open(TASK_NOTES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.task_notes = data.get('task_notes', [])
                    self.current_task = data.get('current_task')
                print(f"[OK] 已加载 {len(self.task_notes)} 条任务笔记")
            
            if os.path.exists(CONTEXT_HISTORY_FILE):
                with open(CONTEXT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.context_history = json.load(f)
                print(f"[OK] 已加载 {len(self.context_history)} 条上下文历史")
        
        except Exception as e:
            print(f"[WARN] 加载持久化数据失败: {str(e)}")
    
    def _save_to_disk(self):
        """保存数据到磁盘"""
        try:
            with open(TASK_NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'task_notes': self.task_notes,
                    'current_task': self.current_task
                }, f, ensure_ascii=False, indent=2)
            
            with open(CONTEXT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.context_history[-100:], f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"[WARN] 保存持久化数据失败: {str(e)}")
    
    def add_task_note(self, note: str, task_id: str = None) -> str:
        """添加任务笔记"""
        task_note = {
            "id": task_id or f"task_{len(self.task_notes) + 1}",
            "note": note,
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress"
        }
        self.task_notes.append(task_note)
        self.current_task = task_note
        self._save_to_disk()
        return task_note["id"]
    
    def update_task_note(self, task_id: str, note: str, status: str = None) -> bool:
        """更新任务笔记"""
        for task in self.task_notes:
            if task["id"] == task_id:
                task["note"] = note
                task["updated_at"] = datetime.now().isoformat()
                if status:
                    task["status"] = status
                self._save_to_disk()
                return True
        return False
    
    def get_task_notes(self, limit: int = 10) -> List[Dict]:
        """获取任务笔记"""
        return self.task_notes[-limit:]
    
    def add_context(self, context: str, context_type: str = "general") -> None:
        """添加上下文"""
        self.context_history.append({
            "content": context,
            "type": context_type,
            "timestamp": datetime.now().isoformat()
        })
        self._save_to_disk()
    
    def clear_old_data(self, days: int = 30):
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.task_notes = [
            task for task in self.task_notes
            if datetime.fromisoformat(task['timestamp']) > cutoff_date
        ]
        
        self.context_history = [
            ctx for ctx in self.context_history
            if datetime.fromisoformat(ctx['timestamp']) > cutoff_date
        ]
        
        self._save_to_disk()
        return f"已清理 {days} 天前的数据"


class MemorySkill(BaseSkill):
    """记忆管理技能"""
    
    def __init__(self):
        super().__init__()
        self.description = "提供任务管理、上下文保存和记忆搜索功能"
        self.memory_manager = MemoryManager()
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """获取技能能力列表"""
        return [
            {
                "name": "create_task_plan",
                "description": "创建任务计划笔记，记录分步骤的任务执行计划",
                "parameters": {
                    "task_description": {"type": "string", "required": True},
                    "steps": {"type": "string", "required": True}
                }
            },
            {
                "name": "update_task_progress",
                "description": "更新任务执行进度",
                "parameters": {
                    "task_id": {"type": "string", "required": True},
                    "current_step": {"type": "string", "required": True},
                    "status": {"type": "string", "required": False, "default": "in_progress"}
                }
            },
            {
                "name": "get_current_task",
                "description": "获取当前任务的详细信息和进度",
                "parameters": {}
            },
            {
                "name": "save_context",
                "description": "保存重要上下文到记忆系统",
                "parameters": {
                    "context": {"type": "string", "required": True},
                    "context_type": {"type": "string", "required": False, "default": "conversation"}
                }
            },
            {
                "name": "get_task_history",
                "description": "获取历史任务记录",
                "parameters": {
                    "limit": {"type": "integer", "required": False, "default": 5}
                }
            },
            {
                "name": "search_memory",
                "description": "搜索记忆中的上下文信息",
                "parameters": {
                    "query": {"type": "string", "required": True},
                    "limit": {"type": "integer", "required": False, "default": 5}
                }
            },
            {
                "name": "clear_old_memory",
                "description": "清理旧的记忆数据",
                "parameters": {
                    "days": {"type": "integer", "required": False, "default": 30}
                }
            },
            {
                "name": "get_memory_stats",
                "description": "获取记忆系统统计信息",
                "parameters": {}
            }
        ]
    
    async def execute(self, capability_name: str, **kwargs) -> Any:
        """执行技能能力"""
        if capability_name == "create_task_plan":
            return self._create_task_plan(**kwargs)
        elif capability_name == "update_task_progress":
            return self._update_task_progress(**kwargs)
        elif capability_name == "get_current_task":
            return self._get_current_task()
        elif capability_name == "save_context":
            return self._save_context(**kwargs)
        elif capability_name == "get_task_history":
            return self._get_task_history(**kwargs)
        elif capability_name == "search_memory":
            return self._search_memory(**kwargs)
        elif capability_name == "clear_old_memory":
            return self._clear_old_memory(**kwargs)
        elif capability_name == "get_memory_stats":
            return self._get_memory_stats()
        else:
            return f"未知能力: {capability_name}"
    
    def _create_task_plan(self, task_description: str, steps: str) -> str:
        """创建任务计划"""
        try:
            note = f"""任务: {task_description}

执行计划:
{steps}

状态: 开始执行
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            task_id = self.memory_manager.add_task_note(note)
            
            return f"""[OK] 任务计划已创建
任务ID: {task_id}
任务: {task_description}

执行步骤:
{steps}

请按照计划逐步执行，并使用 update_task_progress 更新进度。"""
        
        except Exception as e:
            return f"创建任务计划失败: {str(e)}"
    
    def _update_task_progress(self, task_id: str, current_step: str, status: str = "in_progress") -> str:
        """更新任务进度"""
        try:
            task = None
            for t in self.memory_manager.task_notes:
                if str(t["id"]) == str(task_id):
                    task = t
                    break
            
            if not task:
                available_ids = [t["id"] for t in self.memory_manager.task_notes]
                return f"[FAIL] 未找到任务ID: {task_id}\n可用的任务ID: {available_ids}"
            
            updated_note = task["note"] + f"\n\n进度更新 [{datetime.now().strftime('%H:%M:%S')}]:\n{current_step}"
            self.memory_manager.update_task_note(task_id, updated_note, status)
            
            status_emoji = {
                "in_progress": "[PROGRESS]",
                "completed": "[OK]",
                "failed": "[FAIL]"
            }
            
            return f"""{status_emoji.get(status, '📝')} 任务进度已更新
任务ID: {task_id}
当前步骤: {current_step}
状态: {status}"""
        
        except Exception as e:
            return f"更新任务进度失败: {str(e)}"
    
    def _get_current_task(self) -> str:
        """获取当前任务"""
        try:
            if not self.memory_manager.current_task:
                return "当前没有活跃的任务"
            
            task = self.memory_manager.current_task
            return f"""📋 当前任务信息:
任务ID: {task['id']}
状态: {task['status']}
创建时间: {task['timestamp']}

任务详情:
{task['note']}"""
        
        except Exception as e:
            return f"获取当前任务失败: {str(e)}"
    
    def _save_context(self, context: str, context_type: str = "conversation") -> str:
        """保存上下文"""
        try:
            self.memory_manager.add_context(context, context_type)
            
            if len(self.memory_manager.context_history) > 20:
                self.memory_manager.context_history = self.memory_manager.context_history[-10:]
                return f"[OK] 上下文已保存并触发历史压缩\n类型: {context_type}\n内容长度: {len(context)} 字符"
            
            return f"[OK] 上下文已保存\n类型: {context_type}\n内容长度: {len(context)} 字符"
        
        except Exception as e:
            return f"保存上下文失败: {str(e)}"
    
    def _get_task_history(self, limit: int = 5) -> str:
        """获取任务历史"""
        try:
            tasks = self.memory_manager.get_task_notes(limit)
            
            if not tasks:
                return "暂无历史任务记录"
            
            history = f"📚 最近 {len(tasks)} 个任务:\n\n"
            for i, task in enumerate(tasks, 1):
                history += f"{i}. 任务ID: {task['id']}\n"
                history += f"   状态: {task['status']}\n"
                history += f"   时间: {task['timestamp']}\n"
                history += f"   内容: {task['note'][:100]}...\n\n"
            
            return history
        
        except Exception as e:
            return f"获取任务历史失败: {str(e)}"
    
    def _search_memory(self, query: str, limit: int = 5) -> str:
        """搜索记忆"""
        try:
            if not self.memory_manager.context_history:
                return "暂无记忆可搜索"
            
            results = []
            for ctx in self.memory_manager.context_history:
                if query.lower() in ctx['content'].lower():
                    results.append(ctx)
            
            if not results:
                return f"未找到与 '{query}' 相关的记忆"
            
            results = results[-limit:]
            
            memory_text = f"[SEARCH] 找到 {len(results)} 条相关记忆:\n\n"
            for i, ctx in enumerate(results, 1):
                memory_text += f"{i}. [{ctx['type']}] {ctx['content']}\n"
                memory_text += f"   时间: {ctx['timestamp']}\n\n"
            
            return memory_text
        
        except Exception as e:
            return f"搜索记忆失败: {str(e)}"
    
    def _clear_old_memory(self, days: int = 30) -> str:
        """清理旧记忆"""
        try:
            result = self.memory_manager.clear_old_data(days)
            return f"[OK] {result}"
        except Exception as e:
            return f"清理失败: {str(e)}"
    
    def _get_memory_stats(self) -> str:
        """获取记忆统计"""
        try:
            stats = f"""[STATS] 记忆系统统计信息:

任务笔记: {len(self.memory_manager.task_notes)} 条
上下文历史: {len(self.memory_manager.context_history)} 条
当前任务: {'有' if self.memory_manager.current_task else '无'}

存储位置: {MEMORY_STORAGE_DIR}
任务文件: {os.path.exists(TASK_NOTES_FILE)}
上下文文件: {os.path.exists(CONTEXT_HISTORY_FILE)}
"""
            return stats
        except Exception as e:
            return f"获取统计信息失败: {str(e)}"


# 全局单例
_memory_skill_instance = None


def get_memory_skill() -> MemorySkill:
    """获取记忆技能单例"""
    global _memory_skill_instance
    if _memory_skill_instance is None:
        _memory_skill_instance = MemorySkill()
    return _memory_skill_instance
