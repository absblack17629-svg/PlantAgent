# Skill: 记忆管理 (Memory Management)

## 描述
管理任务笔记、对话上下文和长期记忆，支持存储、检索和搜索功能。

## 参数
- `action` (必填): 操作类型
  - `create_task`: 创建新任务笔记
  - `update_task`: 更新任务状态
  - `get_current_task`: 获取当前进行中的任务
  - `save_context`: 保存对话上下文
  - `get_history`: 获取历史任务记录
  - `search`: 搜索记忆内容
  - `clear_old`: 清理过期记忆
  - `stats`: 获取记忆统计

- `task_description` (可选): 任务描述，create_task 时需要
- `task_id` (可选): 任务 ID，update_task 时需要
- `status` (可选): 任务状态，update_task 时可用 (in_progress, completed, failed)
- `context` (可选): 上下文内容，save_context 时需要
- `query` (可选): 搜索关键词，search 时需要
- `limit` (可选): 返回数量限制，默认为 10
- `days` (可选): 保留天数，clear_old 时使用

## 返回值格式
返回 JSON 格式的操作结果，包含:
- `success`: 操作是否成功 (boolean)
- `result`: 操作结果数据 (根据 action 不同而不同)
- `message`: 操作结果描述 (string)

## 使用示例
```
用户要求保存当前任务进度。
1. 调用 skill 时传入 action="create_task", task_description="分析水稻病害图片"
2. 返回: {"success": true, "result": {"id": "task_5", "note": "分析水稻病害图片", "timestamp": "2026-03-08T10:00:00"}, "message": "任务创建成功"}

用户要求搜索之前的相关操作。
1. 调用 skill 时传入 action="search", query="稻瘟病"
2. 返回: {"success": true, "result": [{"note": "分析稻瘟病图片", "timestamp": "..."}], "message": "找到 2 条相关记录"}
```

## 注意事项
- 记忆数据会持久化到磁盘，重启后仍然保留
- 默认只保留最近 100 条上下文记录
- 可以手动清理指定天数之前的旧数据
- 搜索支持模糊匹配和关键词检索