# LangGraph 九节点工作流架构说明

## 概述

现在系统已经使用 **LangGraph** 实现九节点工作流，这是一个更清晰、更专业的架构。

## 为什么使用 LangGraph？

### 之前的问题（手动编排）

```python
# 旧方式：手动管理流程
class NineNodeOrchestrator:
    async def process(self, user_input, image_path):
        # 1. 手动调用每个 Agent
        await intent_agent.step()
        await context_agent.step()
        await memory_agent.step()
        # ... 9 个节点
        
        # 2. 手动管理条件分支
        if intent == "chat":
            # 快速通道
            await response_agent.step()
        else:
            # 完整流程
            await planning_agent.step()
            # ...
```

**问题**：
- 流程逻辑分散在代码中，难以理解
- 条件分支用 if/else，不够清晰
- 难以可视化工作流
- 难以调试和追踪

### 现在的方案（LangGraph）

```python
# 新方式：声明式图结构
workflow = StateGraph(NineNodeState)

# 添加节点
workflow.add_node("intent", intent_node)
workflow.add_node("context", context_node)
# ...

# 定义流程（边）
workflow.add_edge("intent", "context")
workflow.add_conditional_edges(
    "intent",
    should_use_fast_path,
    {
        "fast_path": "response",
        "full_pipeline": "context"
    }
)
```

**优势**：
- ✅ 图结构清晰可见
- ✅ 条件分支用路由函数，逻辑独立
- ✅ 可以可视化工作流
- ✅ 易于调试和追踪
- ✅ 符合行业最佳实践

## 架构图

```
                    ┌─────────┐
                    │  START  │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Intent  │ 意图识别
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ Router  │ 路由判断
                    └─┬─────┬─┘
                      │     │
        快速通道 ◄────┘     └────► 完整流程
              │                    │
         ┌────▼────┐          ┌────▼────┐
         │Response │          │ Context │ 上下文
         └────┬────┘          └────┬────┘
              │                    │
              │               ┌────▼────┐
              │               │ Memory  │ 记忆
              │               └────┬────┘
              │                    │
              │               ┌────▼────┐
              │               │Planning │ 规划
              │               └────┬────┘
              │                    │
              │               ┌────▼────┐
              │               │Validate │ 验证
              │               └─┬─────┬─┘
              │                 │     │
              │        需要澄清 ◄┘     └► 继续
              │                 │         │
              │                 │    ┌────▼────┐
              │                 │    │  Tool   │ 工具执行
              │                 │    └────┬────┘
              │                 │         │
              │                 │    ┌────▼────┐
              │                 │    │ Result  │ 结果验证
              │                 │    └────┬────┘
              │                 │         │
              │                 │    ┌────▼────┐
              │                 │    │   RAG   │ 知识检索
              │                 │    └────┬────┘
              │                 │         │
              └─────────────────┴─────────┘
                                │
                           ┌────▼────┐
                           │Response │ 响应生成
                           └────┬────┘
                                │
                           ┌────▼────┐
                           │   END   │
                           └─────────┘
```

## 核心文件

### 1. 工作流定义
**文件**: `yoloapp/flow/nine_node_graph.py`

```python
# 状态定义
class NineNodeState(TypedDict):
    user_input: str
    image_path: str | None
    intent: str
    emotion: str
    # ... 其他状态字段

# 节点函数
async def intent_node(state: NineNodeState) -> NineNodeState:
    """意图识别节点"""
    # 执行意图识别
    # 更新状态
    return state

# 路由函数
def should_use_fast_path(state: NineNodeState) -> Literal["fast_path", "full_pipeline"]:
    """判断是否使用快速通道"""
    if state["intent"] in ["greet", "goodbye", "chat"]:
        return "fast_path"
    return "full_pipeline"

# 构建图
def create_nine_node_graph() -> StateGraph:
    workflow = StateGraph(NineNodeState)
    
    # 添加节点
    workflow.add_node("intent", intent_node)
    workflow.add_node("context", context_node)
    # ...
    
    # 定义流程
    workflow.add_conditional_edges("intent", should_use_fast_path, {...})
    workflow.add_edge("context", "memory")
    # ...
    
    return workflow.compile()
```

### 2. Agent Factory
**文件**: `routers/agent_factory.py`

```python
async def get_langgraph_app():
    """获取 LangGraph 应用（单例）"""
    from yoloapp.flow.nine_node_graph import create_nine_node_graph
    return create_nine_node_graph()

async def process_agent_request(user_question, image_path):
    """处理请求 - 使用 LangGraph"""
    app = await get_langgraph_app()
    result = await run_nine_node_workflow(user_question, image_path)
    return result
```

### 3. API 路由
**文件**: `routers/langgraph_api.py`

```python
@router.post("/{thread_id}/runs/stream")
async def stream_run(thread_id: str, request: Request):
    """流式运行 - 调用 LangGraph 工作流"""
    result = await process_agent_request(
        user_question=last_user_message,
        image_path=image_path
    )
    # 返回流式响应
```

## 工作流特性

### 1. 状态管理
```python
class NineNodeState(TypedDict):
    # 输入
    user_input: str
    image_path: str | None
    
    # 中间状态
    intent: str
    emotion: str
    context: str
    tool_plan: list[dict]
    tool_results: list[dict]
    
    # 输出
    response: str
```

所有节点共享同一个状态对象，状态在节点间传递。

### 2. 条件路由

```python
# 快速通道 vs 完整流程
workflow.add_conditional_edges(
    "intent",
    should_use_fast_path,
    {
        "fast_path": "response",      # 普通对话直接响应
        "full_pipeline": "context"    # 专业任务走完整流程
    }
)

# 输入验证后的分支
workflow.add_conditional_edges(
    "input_validation",
    should_skip_to_response,
    {
        "skip_to_response": "response",  # 需要澄清
        "continue": "tool_execution"     # 继续执行
    }
)
```

### 3. 节点函数

每个节点都是一个异步函数：

```python
async def intent_node(state: NineNodeState) -> NineNodeState:
    """意图识别节点"""
    # 1. 创建 Agent
    agent = IntentAgent()
    
    # 2. 设置 Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    agent.memory = memory
    
    # 3. 执行 Agent
    await agent.step()
    
    # 4. 更新状态
    state["intent"] = memory.metadata.get("intent", "chat")
    state["emotion"] = memory.metadata.get("emotion", "neutral")
    
    return state
```

## 使用方式

### 1. 直接调用工作流

```python
from yoloapp.flow.nine_node_graph import run_nine_node_workflow

result = await run_nine_node_workflow(
    user_input="水稻稻瘟病怎么防治？",
    image_path=None
)

print(result["response"])
```

### 2. 通过 API

```bash
# LangGraph API
POST http://localhost:8000/threads/{thread_id}/runs/stream

# 或者 MCP Agent API
POST http://localhost:8000/api/mcp/chat
```

### 3. 测试

```bash
python test_langgraph_workflow.py
```

## 优势对比

| 特性 | 手动编排 | LangGraph |
|------|---------|-----------|
| 流程可视化 | ❌ 难 | ✅ 易 |
| 条件分支 | if/else | 路由函数 |
| 调试追踪 | ❌ 困难 | ✅ 清晰 |
| 代码可读性 | ⚠️ 一般 | ✅ 优秀 |
| 维护性 | ⚠️ 一般 | ✅ 优秀 |
| 扩展性 | ⚠️ 一般 | ✅ 优秀 |
| 行业标准 | ❌ 否 | ✅ 是 |

## 迁移说明

### 旧代码（已废弃）

```python
# ❌ 不再使用
from yoloapp.agent import NineNodeOrchestrator
orchestrator = NineNodeOrchestrator()
result = await orchestrator.process(user_input, image_path)
```

### 新代码（推荐）

```python
# ✅ 使用 LangGraph
from yoloapp.flow.nine_node_graph import run_nine_node_workflow
result = await run_nine_node_workflow(user_input, image_path)
```

## 调试技巧

### 1. 查看图结构

```python
from yoloapp.flow.nine_node_graph import create_nine_node_graph

app = create_nine_node_graph()
graph = app.get_graph()

# 查看节点
print(graph.nodes)

# 查看边
print(graph.edges)
```

### 2. 追踪状态变化

```python
# 在节点函数中添加日志
async def intent_node(state: NineNodeState) -> NineNodeState:
    logger.info(f"进入意图节点，输入: {state['user_input']}")
    # ... 处理
    logger.info(f"意图识别结果: {state['intent']}")
    return state
```

### 3. 单独测试节点

```python
from yoloapp.flow.nine_node_graph import intent_node, NineNodeState

state: NineNodeState = {
    "user_input": "你好",
    "image_path": None,
    # ... 其他字段
}

result = await intent_node(state)
print(result["intent"])  # 应该是 "greet"
```

## 下一步

1. ✅ 已完成：LangGraph 工作流实现
2. 🔄 进行中：测试和验证
3. 📋 待办：
   - 添加流式输出支持
   - 添加工作流可视化
   - 优化性能和错误处理
   - 添加更多测试用例

## 总结

使用 LangGraph 后，九节点工作流变得：
- 更清晰：图结构一目了然
- 更专业：符合行业最佳实践
- 更易维护：节点和路由逻辑分离
- 更易扩展：添加新节点或修改流程很简单

这是一个更现代、更优雅的架构！🎉
