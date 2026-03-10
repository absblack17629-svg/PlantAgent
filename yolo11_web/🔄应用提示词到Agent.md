# 🔄 应用提示词到 Agent

## 当前状态

### ✅ 已应用提示词的 Agent
1. **ResponseAgent** - 已应用 `CHAT_SYSTEM_PROMPT` 和响应模板

### ❌ 未应用提示词的 Agent
1. **RAGAgent** - 需要应用 `RAG_SYSTEM_PROMPT`
2. **ContextAgent** - 需要应用 `CONTEXT_SYSTEM_PROMPT`（如果使用 LLM）
3. **MemoryAgent** - 需要应用 `MEMORY_SYSTEM_PROMPT`（如果使用 LLM）
4. **InputValidationAgent** - 需要应用 `INPUT_VALIDATION_SYSTEM_PROMPT`（如果使用 LLM）
5. **ResultValidationAgent** - 需要应用 `RESULT_VALIDATION_SYSTEM_PROMPT`（如果使用 LLM）

## 应用策略

### 策略 1: 基于规则的 Agent（不需要提示词）
这些 Agent 使用基于规则的实现，不调用 LLM：
- IntentAgent - 基于关键词匹配
- PlanningAgent - 基于意图映射
- ToolExecutionAgent - 执行工具调用

### 策略 2: 使用 LLM 的 Agent（需要提示词）
这些 Agent 调用 LLM，需要应用提示词：
- ResponseAgent - ✅ 已应用
- RAGAgent - ❌ 需要应用

### 策略 3: 可选 LLM 的 Agent（预留提示词）
这些 Agent 当前基于规则，但未来可能使用 LLM：
- ContextAgent - 预留提示词
- MemoryAgent - 预留提示词
- InputValidationAgent - 预留提示词
- ResultValidationAgent - 预留提示词

## 应用计划

### 优先级 1: RAGAgent（必须）
**原因**: RAGAgent 直接调用 LLM 生成回答，必须使用专业提示词

**修改内容**:
1. 在 `yoloapp/rag.py` 中应用 `RAG_SYSTEM_PROMPT`
2. 使用 `RAG_QA_TEMPLATE` 格式化问答
3. 使用 `DETECTION_ANALYSIS_TEMPLATE` 分析检测结果

### 优先级 2: 其他 Agent（可选）
**原因**: 当前基于规则，提示词作为未来扩展预留

**策略**: 在代码中添加注释，说明如何使用提示词

## 实施步骤

### 步骤 1: 更新 yoloapp/rag.py
修改 RAG Service 使用新的提示词

### 步骤 2: 测试验证
确保 RAG 回答质量提升

### 步骤 3: 文档更新
更新文档说明提示词应用情况

## 预期效果

### RAG 回答质量提升
- 更专业的角色定位
- 更结构化的回答
- 更完整的信息
- 更实用的建议

### 系统一致性
- 统一的提示词管理
- 一致的回答风格
- 便于维护和优化
