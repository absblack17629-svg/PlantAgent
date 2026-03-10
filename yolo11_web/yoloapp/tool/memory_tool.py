# -*- coding: utf-8 -*-
"""
记忆工具

提供任务管理、上下文保存和记忆搜索功能。
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .base import BaseTool, ToolResult
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


# 持久化存储路径
MEMORY_STORAGE_DIR = "./memory_storage"
TASK_NOTES_FILE = os.path.join(MEMORY_STORAGE_DIR, "task_notes.json")
CONTEXT_HISTORY_FILE = os.path.join(MEMORY_STORAGE_DIR, "context_history.json")


class MemoryManager:
    """记忆管理器（支持持久化）"""
    
    def __init__(self):
        self.task_notes: List[Dict] = []
        self.context_history: List[Dict] = []
        self.current_task: Optional[Dict] = None
        
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
                logger.info(f"已加载 {len(self.task_notes)} 条任务笔记")
            
            if os.path.exists(CONTEXT_HISTORY_FILE):
                with open(CONTEXT_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.context_history = json.load(f)
                logger.info(f"已加载 {len(self.context_history)} 条上下文历史")
        
        except Exception as e:
            logger.warning(f"加载持久化数据失败: {e}")
    
    def _save_to_disk(self):
        """保存数据到磁盘"""
        try:
            with open(TASK_NOTES_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'task_notes': self.task_notes,
                    'current_task': self.current_task
                }, f, ensure_ascii=False, indent=2)
            
            # 只保留最近100条上下文
            with open(CONTEXT_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.context_history[-100:], f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.warning(f"保存持久化数据失败: {e}")
    
    def add_task_note(self, note: str, task_id: Optional[str] = None) -> str:
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
    
    def update_task_note(self, task_id: str, note: str, status: Optional[str] = None) -> bool:
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
    
    def clear_old_data(self, days: int = 30) -> str:
        """清理旧数据"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        old_task_count = len(self.task_notes)
        old_context_count = len(self.context_history)
        
        self.task_notes = [
            task for task in self.task_notes
            if datetime.fromisoformat(task['timestamp']) > cutoff_date
        ]
        
        self.context_history = [
            ctx for ctx in self.context_history
            if datetime.fromisoformat(ctx['timestamp']) > cutoff_date
        ]
        
        self._save_to_disk()
        
        removed_tasks = old_task_count - len(self.task_notes)
        removed_contexts = old_context_count - len(self.context_history)
        
        return f"已清理 {removed_tasks} 条任务和 {removed_contexts} 条上下文"


# 全局单例
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """获取记忆管理器单例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


class MemoryTool(BaseTool):
    """记忆管理工具
    
    提供任务管理、上下文保存和记忆搜索功能。
    """
    
    name: str = "manage_memory"
    description: str = "管理任务笔记、上下文和记忆"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "操作类型",
                "enum": [
                    "create_task",
                    "update_task",
                    "get_current_task",
                    "save_context",
                    "get_history",
                    "search",
                    "clear_old",
                    "stats"
                ]
            },
            "task_description": {
                "type": "string",
                "description": "任务描述（create_task 时需要）"
            },
            "steps": {
                "type": "string",
                "description": "任务步骤（create_task 时需要）"
            },
            "task_id": {
                "type": "string",
                "description": "任务ID（update_task 时需要）"
            },
            "current_step": {
                "type": "string",
                "description": "当前步骤（update_task 时需要）"
            },
            "status": {
                "type": "string",
                "description": "任务状态（update_task 时可选）",
                "enum": ["in_progress", "completed", "failed"]
            },
            "context": {
                "type": "string",
                "description": "上下文内容（save_context 时需要）"
            },
            "context_type": {
                "type": "string",
                "description": "上下文类型（save_context 时可选）"
            },
            "query": {
                "type": "string",
                "description": "搜索查询（search 时需要）"
            },
            "limit": {
                "type": "integer",
                "description": "限制数量"
            },
            "days": {
                "type": "integer",
                "description": "天数（clear_old 时需要）"
            }
        },
        "required": ["action"]
    }
    
    memory_manager: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化记忆工具"""
        super().__init__(**data)
        
        if self.memory_manager is None:
            self.memory_manager = get_memory_manager()
        
        logger.info(f"初始化记忆工具: {self.name}")
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """执行记忆管理操作
        
        Args:
            action: 操作类型
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 操作结果
        """
        try:
            if action == "create_task":
                return await self._create_task(**kwargs)
            elif action == "update_task":
                return await self._update_task(**kwargs)
            elif action == "get_current_task":
                return await self._get_current_task()
            elif action == "save_context":
                return await self._save_context(**kwargs)
            elif action == "get_history":
                return await self._get_history(**kwargs)
            elif action == "search":
                return await self._search(**kwargs)
            elif action == "clear_old":
                return await self._clear_old(**kwargs)
            elif action == "stats":
                return await self._get_stats()
            else:
                return self.fail_response(
                    error=f"不支持的操作: {action}",
                    error_code="INVALID_ACTION"
                )
        
        except Exception as e:
            logger.error(f"记忆操作失败: {e}", exc_info=True)
            return self.fail_response(
                error=f"记忆操作失败: {str(e)}",
                error_code="MEMORY_OPERATION_FAILED"
            )
    
    async def _create_task(
        self,
        task_description: str,
        steps: str,
        **kwargs
    ) -> ToolResult:
        """创建任务计划"""
        note = f"""任务: {task_description}

执行计划:
{steps}

状态: 开始执行
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        task_id = self.memory_manager.add_task_note(note)
        
        result_text = f"""[OK] 任务计划已创建
任务ID: {task_id}
任务: {task_description}

执行步骤:
{steps}

请按照计划逐步执行，并使用 update_task_progress 更新进度。"""
        
        return self.success_response(
            data={
                "task_id": task_id,
                "task_description": task_description,
                "steps": steps
            },
            message=result_text
        )
    
    async def _update_task(
        self,
        task_id: str,
        current_step: str,
        status: str = "in_progress",
        **kwargs
    ) -> ToolResult:
        """更新任务进度"""
        task = None
        for t in self.memory_manager.task_notes:
            if str(t["id"]) == str(task_id):
                task = t
                break
        
        if not task:
            available_ids = [t["id"] for t in self.memory_manager.task_notes]
            return self.fail_response(
                error=f"未找到任务ID: {task_id}",
                error_code="TASK_NOT_FOUND",
                available_ids=available_ids
            )
        
        updated_note = task["note"] + f"\n\n进度更新 [{datetime.now().strftime('%H:%M:%S')}]:\n{current_step}"
        self.memory_manager.update_task_note(task_id, updated_note, status)
        
        status_emoji = {
            "in_progress": "[PROGRESS]",
            "completed": "[OK]",
            "failed": "[FAIL]"
        }
        
        result_text = f"""{status_emoji.get(status, '📝')} 任务进度已更新
任务ID: {task_id}
当前步骤: {current_step}
状态: {status}"""
        
        return self.success_response(
            data={
                "task_id": task_id,
                "current_step": current_step,
                "status": status
            },
            message=result_text
        )
    
    async def _get_current_task(self) -> ToolResult:
        """获取当前任务"""
        if not self.memory_manager.current_task:
            return self.success_response(
                data=None,
                message="当前没有活跃的任务"
            )
        
        task = self.memory_manager.current_task
        result_text = f"""📋 当前任务信息:
任务ID: {task['id']}
状态: {task['status']}
创建时间: {task['timestamp']}

任务详情:
{task['note']}"""
        
        return self.success_response(
            data=task,
            message=result_text
        )
    
    async def _save_context(
        self,
        context: str,
        context_type: str = "conversation",
        **kwargs
    ) -> ToolResult:
        """保存上下文"""
        self.memory_manager.add_context(context, context_type)
        
        if len(self.memory_manager.context_history) > 20:
            self.memory_manager.context_history = self.memory_manager.context_history[-10:]
            message = f"[OK] 上下文已保存并触发历史压缩\n类型: {context_type}\n内容长度: {len(context)} 字符"
        else:
            message = f"[OK] 上下文已保存\n类型: {context_type}\n内容长度: {len(context)} 字符"
        
        return self.success_response(
            data={
                "context_type": context_type,
                "length": len(context)
            },
            message=message
        )
    
    async def _get_history(self, limit: int = 5, **kwargs) -> ToolResult:
        """获取任务历史"""
        tasks = self.memory_manager.get_task_notes(limit)
        
        if not tasks:
            return self.success_response(
                data=[],
                message="暂无历史任务记录"
            )
        
        history_text = f"📚 最近 {len(tasks)} 个任务:\n\n"
        for i, task in enumerate(tasks, 1):
            history_text += f"{i}. 任务ID: {task['id']}\n"
            history_text += f"   状态: {task['status']}\n"
            history_text += f"   时间: {task['timestamp']}\n"
            history_text += f"   内容: {task['note'][:100]}...\n\n"
        
        return self.success_response(
            data=tasks,
            message=history_text
        )
    
    async def _search(self, query: str, limit: int = 5, **kwargs) -> ToolResult:
        """搜索记忆"""
        if not self.memory_manager.context_history:
            return self.success_response(
                data=[],
                message="暂无记忆可搜索"
            )
        
        results = []
        for ctx in self.memory_manager.context_history:
            if query.lower() in ctx['content'].lower():
                results.append(ctx)
        
        if not results:
            return self.success_response(
                data=[],
                message=f"未找到与 '{query}' 相关的记忆"
            )
        
        results = results[-limit:]
        
        memory_text = f"[SEARCH] 找到 {len(results)} 条相关记忆:\n\n"
        for i, ctx in enumerate(results, 1):
            memory_text += f"{i}. [{ctx['type']}] {ctx['content']}\n"
            memory_text += f"   时间: {ctx['timestamp']}\n\n"
        
        return self.success_response(
            data=results,
            message=memory_text
        )
    
    async def _clear_old(self, days: int = 30, **kwargs) -> ToolResult:
        """清理旧记忆"""
        result = self.memory_manager.clear_old_data(days)
        return self.success_response(
            data={"days": days},
            message=f"[OK] {result}"
        )
    
    async def _get_stats(self) -> ToolResult:
        """获取记忆统计"""
        stats_text = f"""[STATS] 记忆系统统计信息:

任务笔记: {len(self.memory_manager.task_notes)} 条
上下文历史: {len(self.memory_manager.context_history)} 条
当前任务: {'有' if self.memory_manager.current_task else '无'}

存储位置: {MEMORY_STORAGE_DIR}
任务文件: {os.path.exists(TASK_NOTES_FILE)}
上下文文件: {os.path.exists(CONTEXT_HISTORY_FILE)}
"""
        
        return self.success_response(
            data={
                "task_count": len(self.memory_manager.task_notes),
                "context_count": len(self.memory_manager.context_history),
                "has_current_task": self.memory_manager.current_task is not None,
                "storage_dir": MEMORY_STORAGE_DIR
            },
            message=stats_text
        )


# 工厂函数
def get_memory_tool() -> MemoryTool:
    """获取记忆工具实例"""
    return MemoryTool()
