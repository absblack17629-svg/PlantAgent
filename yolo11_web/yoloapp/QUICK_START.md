# 🚀 YOLOApp 快速入门指南

欢迎使用 YOLOApp！这是一个 5 分钟快速入门指南，帮助你立即开始使用新的模块化结构。

---

## 📦 什么是 YOLOApp？

YOLOApp 是按照 OpenManus 风格重新组织的代码结构，提供：
- ✅ 更清晰的模块组织
- ✅ 更短的导入路径
- ✅ 更好的可维护性
- ✅ 完全向后兼容

---

## 🎯 立即开始

### 1️⃣ 基础导入

**Agent 模块：**
```python
# 导入 Agent 基类和具体实现
from yoloapp.agent import (
    BaseAgent,           # Agent 基类
    IntentAgent,         # 意图理解
    ContextAgent,        # 上下文管理
    MemoryAgent,         # 记忆管理
    PlanningAgent,       # 工具规划
    NineNodeOrchestrator,  # 九节点编排器
    create_nine_node_orchestrator  # 工厂函数
)

# 使用示例
agent = IntentAgent(name="intent_agent")
orchestrator = create_nine_node_orchestrator()
```

**Schema 模块：**
```python
# 导入数据模型
from yoloapp.schema import (
    AgentRole,      # Agent 角色枚举
    AgentState,     # Agent 状态枚举
    Message,        # 消息模型
    Memory,         # 记忆模型
    ToolResult,     # 工具结果
    ToolCall        # 工具调用
)

# 使用示例
message = Message.user_message("你好")
memory = Memory()
memory.add_message(message)
```

**异常处理：**
```python
# 导入异常类
from yoloapp.exceptions import (
    AgentError,      # Agent 基础异常
    DetectionError,  # 检测异常
    RAGError,        # RAG 异常
    ToolError,       # 工具异常
    FlowError        # 流程异常
)

# 使用示例
try:
    result = await agent.run(request)
except AgentError as e:
    print(f"Agent 错误: {e.message}")
```

### 2️⃣ 创建一个简单的 Agent

```python
# example_agent.py
from yoloapp.agent import BaseAgent
from yoloapp.schema import AgentRole, Message

class MyAgent(BaseAgent):
    """自定义 Agent 示例"""
    
    def __init__(self, name: str = "my_agent"):
        super().__init__(
            name=name,
            role=AgentRole.GENERAL,
            description="我的第一个 Agent"
        )
    
    async def step(self) -> str:
        """执行单步操作"""
        # 获取用户输入
        user_message = self.memory.get_recent_messages(1)[0]
        
        # 处理逻辑
        response = f"收到消息: {user_message.content}"
        
        # 更新记忆
        self.update_memory("assistant", response)
        
        # 标记完成
        self.mark_finished()
        
        return response

# 使用 Agent
async def main():
    agent = MyAgent()
    result = await agent.run("你好，世界！")
    print(result)

# 运行
import asyncio
asyncio.run(main())
```

### 3️⃣ 使用九节点编排器

```python
# example_orchestrator.py
from yoloapp.agent import create_nine_node_orchestrator

async def main():
    # 创建编排器
    orchestrator = create_nine_node_orchestrator()
    
    # 处理用户输入
    result = await orchestrator.process("检测这张图片的病害")
    
    # 查看结果
    print(f"意图: {result.get('intent')}")
    print(f"响应: {result.get('response')}")

import asyncio
asyncio.run(main())
```

### 4️⃣ 使用工具

```python
# example_tool.py
from yoloapp.tool import BaseTool, MemoryTool
from yoloapp.schema import ToolResult

# 使用现有工具
memory_tool = MemoryTool()
result = await memory_tool(action="get", key="user_context")

# 创建自定义工具
class MyTool(BaseTool):
    """自定义工具示例"""
    
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的第一个工具"
        )
    
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        try:
            # 工具逻辑
            data = kwargs.get("data", "")
            result = f"处理结果: {data}"
            
            return self.success_response(result)
        except Exception as e:
            return self.fail_response(str(e))

# 使用工具
tool = MyTool()
result = await tool(data="测试数据")
if result.success:
    print(result.output)
```

---

## 🔄 从旧代码迁移

### 迁移步骤

**步骤 1: 更新导入语句**

```python
# ❌ 旧代码
from services.agents import BaseAgent
from schemas.message import Message
from services.exceptions import AgentError

# ✅ 新代码
from yoloapp.agent import BaseAgent
from yoloapp.schema import Message
from yoloapp.exceptions import AgentError
```

**步骤 2: 运行测试**

```bash
# 运行测试确保功能正常
python -m pytest tests/
```

**步骤 3: 清理警告**

旧的导入路径会显示 DeprecationWarning，逐步更新即可。

### 完整的导入映射

| 旧路径 | 新路径 |
|--------|--------|
| `services.agents.*` | `yoloapp.agent.*` |
| `services.tools.*` | `yoloapp.tool.*` |
| `services.flows.*` | `yoloapp.flow.*` |
| `schemas.*` | `yoloapp.schema` |
| `prompts.*` | `yoloapp.prompt.*` |
| `services.exceptions` | `yoloapp.exceptions` |
| `services.config` | `yoloapp.config` |
| `utils.logger` | `yoloapp.utils.logger` |

---

## 📝 常用代码片段

### 创建消息

```python
from yoloapp.schema import Message

# 用户消息
user_msg = Message.user_message("你好")

# 系统消息
system_msg = Message.system_message("你是一个助手")

# 助手消息
assistant_msg = Message.assistant_message("你好！")
```

### 管理记忆

```python
from yoloapp.schema import Memory, Message

memory = Memory()

# 添加消息
memory.add_message(Message.user_message("问题1"))
memory.add_message(Message.assistant_message("回答1"))

# 获取最近消息
recent = memory.get_recent_messages(5)

# 清空记忆
memory.clear()
```

### 异常处理

```python
from yoloapp.exceptions import AgentError, DetectionError

try:
    result = await agent.run(request)
except DetectionError as e:
    print(f"检测失败: {e.message}")
    print(f"错误代码: {e.error_code}")
    print(f"上下文: {e.context}")
except AgentError as e:
    print(f"Agent 错误: {e.message}")
```

### 使用配置

```python
from yoloapp.config import get_config_manager

# 获取配置管理器
config = get_config_manager()

# 访问配置
llm_config = config.llm
yolo_config = config.yolo
rag_config = config.rag

print(f"LLM 模型: {llm_config['model']}")
print(f"YOLO 模型: {yolo_config['model_path']}")
```

---

## 🎓 学习资源

### 核心文档

1. **MIGRATION_GUIDE.md** - 详细迁移指南
   - 完整的导入映射表
   - 10+ 代码示例
   - 常见问题解答

2. **AGENTS.md** - 开发者文档
   - YOLOApp 架构说明
   - 代码风格指南
   - 测试指南

3. **.kiro/specs/yoloapp-migration/** - 完整 Spec
   - 需求文档
   - 设计文档
   - 任务列表

### 示例代码

查看这些文件了解更多示例：
- `test_yoloapp_imports.py` - 导入示例
- `test_backward_compatibility.py` - 兼容性示例
- `yoloapp/agent/` - Agent 实现示例
- `yoloapp/tool/` - Tool 实现示例

---

## ✅ 快速检查清单

使用这个清单确保你已经准备好：

- [ ] 阅读了本快速入门指南
- [ ] 理解了新的导入路径
- [ ] 尝试了基础导入示例
- [ ] 创建了第一个使用 yoloapp 的文件
- [ ] 运行了测试验证功能正常
- [ ] 查看了 MIGRATION_GUIDE.md 了解更多细节

---

## 🆘 需要帮助？

### 常见问题

**Q: 旧代码还能用吗？**
A: 能！所有旧的导入路径继续工作，只是会显示 DeprecationWarning。

**Q: 必须立即迁移吗？**
A: 不必！可以逐步迁移，新代码使用新路径，旧代码继续工作。

**Q: 如何处理废弃警告？**
A: 按照警告信息更新导入路径即可，或者暂时忽略警告。

**Q: 迁移会破坏现有功能吗？**
A: 不会！新旧导入指向完全相同的对象，功能完全一致。

### 获取更多帮助

1. 查看 `MIGRATION_GUIDE.md` 获取详细指南
2. 查看 `AGENTS.md` 了解架构说明
3. 运行测试脚本验证功能：`python test_yoloapp_imports.py`

---

## 🎉 开始使用！

现在你已经准备好使用 YOLOApp 了！

**推荐的第一步：**
1. 创建一个新的测试文件
2. 尝试导入 yoloapp 模块
3. 创建一个简单的 Agent
4. 运行并查看结果

```python
# my_first_yoloapp.py
from yoloapp.agent import IntentAgent
from yoloapp.schema import Message

async def main():
    agent = IntentAgent(name="test")
    result = await agent.run("你好，YOLOApp！")
    print(result)

import asyncio
asyncio.run(main())
```

**祝你使用愉快！** 🚀

---

*快速入门指南版本: 1.0*  
*最后更新: 2026-03-07*
