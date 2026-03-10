# YOLOApp 迁移指南

本文档提供从旧代码结构迁移到新 yoloapp/ 结构的完整指南。

## 目录

1. [目录结构对比](#目录结构对比)
2. [导入路径映射](#导入路径映射)
3. [代码迁移示例](#代码迁移示例)
4. [常见问题解答](#常见问题解答)
5. [迁移检查清单](#迁移检查清单)

## 目录结构对比

### 旧结构 → 新结构

```
旧结构                          新结构 (yoloapp/)
─────────────────────────────────────────────────────────
services/                       yoloapp/
├── agents/                     ├── agent/
│   ├── base.py                 │   ├── base.py
│   ├── intent_agent.py         │   ├── intent_agent.py
│   ├── context_agent.py        │   ├── context_agent.py
│   ├── memory_agent.py         │   ├── memory_agent.py
│   ├── planning_agent.py       │   ├── planning_agent.py
│   ├── input_validation_agent.py│  ├── input_validation_agent.py
│   ├── tool_execution_agent.py │   ├── tool_execution_agent.py
│   ├── result_validation_agent.py│  ├── result_validation_agent.py
│   ├── rag_agent.py            │   ├── rag_agent.py
│   ├── response_agent.py       │   ├── response_agent.py
│   ├── nine_node_orchestrator.py│  ├── orchestrator.py
│   ├── detection_agent.py      │   ├── detection_agent.py
│   └── knowledge_agent.py      │   └── knowledge_agent.py
│                               │
├── tools/                      ├── tool/
│   ├── base.py                 │   ├── base.py
│   ├── detection_tool.py       │   ├── detection_tool.py
│   ├── knowledge_tool.py       │   ├── knowledge_tool.py
│   └── memory_tool.py          │   └── memory_tool.py
│                               │
├── flows/                      ├── flow/
│   ├── base.py                 │   ├── base.py
│   ├── detection_flow.py       │   ├── detection_flow.py
│   └── knowledge_flow.py       │   └── knowledge_flow.py
│                               │
├── llm/                        ├── llm.py (合并)
│   ├── client.py               │
│   └── token_counter.py        │
│                               │
├── exceptions.py               ├── exceptions.py
├── config.py                   ├── config.py
└── rag_service.py              └── rag.py
                                │
prompts/                        ├── prompt/
├── rag_prompts.py              │   ├── rag_prompts.py
├── rice_disease_prompts.py     │   ├── rice_disease_prompts.py
└── planning.py                 │   └── planning.py
                                │
schemas/                        ├── schema.py (合并)
├── agent.py                    │
├── message.py                  │
└── tool.py                     │
                                │
utils/                          └── utils/
└── logger.py                       └── logger.py
```

## 导入路径映射

### Agent 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from services.agents.base import BaseAgent` | `from yoloapp.agent import BaseAgent` |
| `from services.agents.intent_agent import IntentAgent` | `from yoloapp.agent import IntentAgent` |
| `from services.agents.context_agent import ContextAgent` | `from yoloapp.agent import ContextAgent` |
| `from services.agents.memory_agent import MemoryAgent` | `from yoloapp.agent import MemoryAgent` |
| `from services.agents.planning_agent import PlanningAgent` | `from yoloapp.agent import PlanningAgent` |
| `from services.agents.input_validation_agent import InputValidationAgent` | `from yoloapp.agent import InputValidationAgent` |
| `from services.agents.tool_execution_agent import ToolExecutionAgent` | `from yoloapp.agent import ToolExecutionAgent` |
| `from services.agents.result_validation_agent import ResultValidationAgent` | `from yoloapp.agent import ResultValidationAgent` |
| `from services.agents.rag_agent import RAGAgent` | `from yoloapp.agent import RAGAgent` |
| `from services.agents.response_agent import ResponseAgent` | `from yoloapp.agent import ResponseAgent` |
| `from services.agents.nine_node_orchestrator import NineNodeOrchestrator` | `from yoloapp.agent import NineNodeOrchestrator` |
| `from services.agents.detection_agent import DetectionAgent` | `from yoloapp.agent.detection_agent import DetectionAgent` |
| `from services.agents.knowledge_agent import KnowledgeAgent` | `from yoloapp.agent.knowledge_agent import KnowledgeAgent` |

### Tool 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from services.tools.base import BaseTool` | `from yoloapp.tool import BaseTool` |
| `from services.tools.detection_tool import DetectionTool` | `from yoloapp.tool.detection_tool import DetectionTool` |
| `from services.tools.knowledge_tool import KnowledgeTool` | `from yoloapp.tool.knowledge_tool import KnowledgeTool` |
| `from services.tools.memory_tool import MemoryTool` | `from yoloapp.tool import MemoryTool` |

### Flow 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from services.flows.base import BaseFlow` | `from yoloapp.flow import BaseFlow` |
| `from services.flows.detection_flow import DetectionFlow` | `from yoloapp.flow.detection_flow import DetectionFlow` |
| `from services.flows.knowledge_flow import KnowledgeFlow` | `from yoloapp.flow.knowledge_flow import KnowledgeFlow` |

### Schema 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from schemas.agent import AgentRole, AgentState, AgentConfig` | `from yoloapp.schema import AgentRole, AgentState, AgentConfig` |
| `from schemas.message import Message, Memory` | `from yoloapp.schema import Message, Memory` |
| `from schemas.tool import ToolResult, ToolCall, ToolParameter` | `from yoloapp.schema import ToolResult, ToolCall, ToolParameter` |

### 异常模块

| 旧路径 | 新路径 |
|--------|--------|
| `from services.exceptions import AgentError` | `from yoloapp.exceptions import AgentError` |
| `from services.exceptions import DetectionError` | `from yoloapp.exceptions import DetectionError` |
| `from services.exceptions import RAGError` | `from yoloapp.exceptions import RAGError` |
| `from services.exceptions import ToolError` | `from yoloapp.exceptions import ToolError` |
| `from services.exceptions import FlowError` | `from yoloapp.exceptions import FlowError` |

### 配置和服务模块

| 旧路径 | 新路径 |
|--------|--------|
| `from services.config import get_config_manager` | `from yoloapp.config import get_config_manager` |
| `from services.rag_service import RAGService` | `from yoloapp.rag import RAGService` |
| `from services.llm.client import LLMClient` | `from yoloapp.llm import LLMClient` |
| `from services.llm.token_counter import TokenCounter` | `from yoloapp.llm import TokenCounter` |

### Prompt 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from prompts.rag_prompts import RAG_QA_TEMPLATE` | `from yoloapp.prompt.rag_prompts import RAG_QA_TEMPLATE` |
| `from prompts.rice_disease_prompts import DISEASE_PROMPT` | `from yoloapp.prompt.rice_disease_prompts import DISEASE_PROMPT` |
| `from prompt.planning import PLANNING_PROMPT` | `from yoloapp.prompt.planning import PLANNING_PROMPT` |

### Utils 模块

| 旧路径 | 新路径 |
|--------|--------|
| `from utils.logger import get_logger` | `from yoloapp.utils import get_logger` |

## 代码迁移示例

### 示例 1: 创建九节点编排器

**旧代码:**
```python
from services.agents.nine_node_orchestrator import create_nine_node_orchestrator

orchestrator = create_nine_node_orchestrator()
result = await orchestrator.process("用户输入")
```

**新代码:**
```python
from yoloapp.agent import create_nine_node_orchestrator

orchestrator = create_nine_node_orchestrator()
result = await orchestrator.process("用户输入")
```

### 示例 2: 使用检测工具

**旧代码:**
```python
from services.tools.detection_tool import DetectionTool
from schemas.tool import ToolResult

tool = DetectionTool()
result: ToolResult = await tool(image_path="test.jpg")
if result.success:
    print(result.output)
```

**新代码:**
```python
from yoloapp.tool.detection_tool import DetectionTool
from yoloapp.schema import ToolResult

tool = DetectionTool()
result: ToolResult = await tool(image_path="test.jpg")
if result.success:
    print(result.output)
```

### 示例 3: 创建自定义 Agent

**旧代码:**
```python
from services.agents.base import BaseAgent
from schemas.agent import AgentRole, AgentConfig
from schemas.message import Message

class MyAgent(BaseAgent):
    async def step(self) -> str:
        # 实现逻辑
        self.mark_finished()
        return "Done"

config = AgentConfig(role=AgentRole.GENERAL)
agent = MyAgent(config=config)
```

**新代码:**
```python
from yoloapp.agent import BaseAgent
from yoloapp.schema import AgentRole, AgentConfig, Message

class MyAgent(BaseAgent):
    async def step(self) -> str:
        # 实现逻辑
        self.mark_finished()
        return "Done"

config = AgentConfig(role=AgentRole.GENERAL)
agent = MyAgent(config=config)
```

### 示例 4: 使用检测流程

**旧代码:**
```python
from services.flows.detection_flow import create_detection_flow

flow = create_detection_flow(
    confidence_threshold=0.6,
    auto_query_knowledge=True
)
result = await flow.execute({
    "image_path": "test.jpg",
    "user_query": "检测病害"
})
```

**新代码:**
```python
from yoloapp.flow.detection_flow import create_detection_flow

flow = create_detection_flow(
    confidence_threshold=0.6,
    auto_query_knowledge=True
)
result = await flow.execute({
    "image_path": "test.jpg",
    "user_query": "检测病害"
})
```

### 示例 5: 异常处理

**旧代码:**
```python
from services.exceptions import AgentError, DetectionError
from utils.logger import get_logger

logger = get_logger(__name__)

try:
    result = await agent.run(request)
except DetectionError as e:
    logger.error(f"检测失败: {e.message}")
except AgentError as e:
    logger.error(f"Agent 错误: {e.message}")
```

**新代码:**
```python
from yoloapp.exceptions import AgentError, DetectionError
from yoloapp.utils import get_logger

logger = get_logger(__name__)

try:
    result = await agent.run(request)
except DetectionError as e:
    logger.error(f"检测失败: {e.message}")
except AgentError as e:
    logger.error(f"Agent 错误: {e.message}")
```

## 常见问题解答

### Q1: 为什么有些模块不能从包级别导入？

A: 某些模块（如 DetectionAgent, KnowledgeAgent, DetectionTool, KnowledgeTool, DetectionFlow, KnowledgeFlow）依赖外部服务（DetectionService, RAGService），这些服务可能有复杂的依赖或初始化要求。为了避免导入时的副作用，这些模块采用延迟导入策略，需要时单独导入。

**示例:**
```python
# ❌ 不能这样导入
from yoloapp.agent import DetectionAgent  # ImportError

# ✅ 应该这样导入
from yoloapp.agent.detection_agent import DetectionAgent
```

### Q2: 旧的导入路径还能用吗？

A: 目前旧的导入路径仍然可用，但会在未来版本中废弃。建议尽快迁移到新路径。

### Q3: 如何批量更新导入路径？

A: 可以使用以下正则表达式进行批量替换：

```regex
# Agent 模块
from services\.agents\.(\w+) import -> from yoloapp.agent.\1 import
from services\.agents import -> from yoloapp.agent import

# Tool 模块
from services\.tools\.(\w+) import -> from yoloapp.tool.\1 import
from services\.tools import -> from yoloapp.tool import

# Flow 模块
from services\.flows\.(\w+) import -> from yoloapp.flow.\1 import
from services\.flows import -> from yoloapp.flow import

# Schema 模块
from schemas\.(\w+) import -> from yoloapp.schema import

# 异常模块
from services\.exceptions import -> from yoloapp.exceptions import

# Utils 模块
from utils\.logger import -> from yoloapp.utils import
```

### Q4: 新结构有什么优势？

A: 新结构的优势包括：

1. **清晰的模块划分** - 按功能模块组织代码，更容易理解和维护
2. **符合 OpenManus 风格** - 遵循业界最佳实践
3. **更好的包管理** - 每个子包都有明确的 __init__.py 和 __all__ 定义
4. **简化的导入** - 可以从包级别导入常用类，减少导入语句长度
5. **更好的文档** - 每个模块都有清晰的文档字符串

### Q5: 如何处理循环导入问题？

A: 新结构通过以下方式避免循环导入：

1. 使用延迟导入（在函数内部导入）
2. 使用类型注解的字符串形式（`"ClassName"` 而不是 `ClassName`）
3. 将共享的类型定义放在 schema.py 中

## 迁移检查清单

使用此检查清单确保迁移完整：

### 代码迁移

- [ ] 更新所有 Agent 相关导入
- [ ] 更新所有 Tool 相关导入
- [ ] 更新所有 Flow 相关导入
- [ ] 更新所有 Schema 相关导入
- [ ] 更新所有异常处理导入
- [ ] 更新所有配置和服务导入
- [ ] 更新所有 Prompt 相关导入
- [ ] 更新所有 Utils 相关导入

### 测试验证

- [ ] 运行所有单元测试
- [ ] 运行所有集成测试
- [ ] 测试 API 端点
- [ ] 测试 FastAPI 服务启动
- [ ] 验证日志输出正常
- [ ] 验证错误处理正常

### 文档更新

- [ ] 更新 README.md
- [ ] 更新 AGENTS.md
- [ ] 更新 API 文档
- [ ] 更新代码注释
- [ ] 更新示例代码

### 清理工作

- [ ] 删除未使用的导入
- [ ] 删除未使用的文件
- [ ] 更新 .gitignore
- [ ] 更新依赖列表

## 获取帮助

如果在迁移过程中遇到问题：

1. 查看本文档的常见问题解答部分
2. 查看 yoloapp/ 目录下各模块的文档字符串
3. 运行测试脚本 `python test_yoloapp_imports.py` 验证导入
4. 查看 AGENTS.md 了解新架构的详细信息

## 版本历史

- **v1.0.0** (2026-03-07) - 初始版本，完成基础迁移
