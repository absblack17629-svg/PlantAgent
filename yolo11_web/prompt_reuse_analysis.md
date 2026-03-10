# OpenManus 提示词复用分析

## 当前系统架构回顾

你的水稻病害检测系统使用九节点工作流：
1. IntentSkillAgent - 意图理解 + 情感分析
2. ContextSkillAgent - 上下文管理
3. MemorySkillAgent - 对话记忆
4. PlanningSkillAgent - 工具规划
5. InputValidationAgent - 输入验证
6. ToolExecutionAgent - 工具执行
7. ResultValidationAgent - 结果验证
8. RAGSkillAgent - RAG检索
9. ResponseSkillAgent - 响应生成

## OpenManus 提示词分析

### 1. ✅ planning.py - 强烈推荐复用

**用途：** 规划 Agent 的系统提示词

**可复用到：** PlanningSkillAgent（节点4）

**复用价值：** ⭐⭐⭐⭐⭐

**原因：**
- 提供了清晰的规划流程：分析 → 创建计划 → 执行 → 跟踪 → 完成
- 强调任务分解和依赖关系
- 包含进度跟踪和计划调整机制
- 明确何时结束任务

**建议修改：**
```python
# 原始提示词
PLANNING_SYSTEM_PROMPT = """
You are an expert Planning Agent tasked with solving problems efficiently through structured plans.
Your job is:
1. Analyze requests to understand the task scope
2. Create a clear, actionable plan that makes meaningful progress with the `planning` tool
3. Execute steps using available tools as needed
4. Track progress and adapt plans when necessary
5. Use `finish` to conclude immediately when the task is complete
"""

# 适配到水稻病害检测系统
RICE_DISEASE_PLANNING_PROMPT = """
你是水稻病害检测系统的规划专家，负责高效地制定结构化计划。
你的职责：
1. 分析用户请求，理解任务范围（病害检测、知识查询、防治建议等）
2. 创建清晰可执行的计划，选择合适的技能（DetectionSkill、KnowledgeSkill、MemorySkill）
3. 根据需要执行计划步骤
4. 跟踪进度并在必要时调整计划
5. 任务完成后立即结束

可用技能：
- DetectionSkill: 图片病害检测
- KnowledgeSkill: 农业知识查询和病害分析
- MemorySkill: 对话历史管理

将任务分解为逻辑步骤，考虑依赖关系和验证方法。
知道何时结束 - 目标达成后不要继续思考。
"""
```

---

### 2. ✅ toolcall.py - 可以复用

**用途：** 工具调用 Agent 的基础提示词

**可复用到：** ToolExecutionAgent（节点6）

**复用价值：** ⭐⭐⭐⭐

**原因：**
- 简洁明了的工具执行指导
- 包含终止机制

**建议修改：**
```python
# 适配版本
TOOL_EXECUTION_PROMPT = """
你是工具执行专家，负责调用各种技能完成任务。

可用技能：
- DetectionSkill.detect_objects: 检测图片中的病害
- KnowledgeSkill.query_knowledge: 查询农业知识
- KnowledgeSkill.analyze_detection: 分析检测结果
- MemorySkill.save_context: 保存对话上下文
- MemorySkill.get_recent_context: 获取最近对话

执行规则：
1. 根据计划选择合适的技能和能力
2. 提供正确格式的参数
3. 观察执行结果并判断是否成功
4. 最多重试2次
5. 如果需要停止交互，使用 `terminate` 工具调用
"""
```

---

### 3. ⚠️ manus.py - 部分复用

**用途：** 通用 AI 助手的系统提示词

**可复用到：** ResponseSkillAgent（节点9）或整体系统提示

**复用价值：** ⭐⭐⭐

**原因：**
- 提供了友好的助手定位
- 强调工具选择和任务分解
- 包含执行结果解释

**建议修改：**
```python
# 适配版本
RICE_DISEASE_SYSTEM_PROMPT = """
你是水稻病害智能助手，专注于解决用户提出的水稻病害相关任务。
你拥有多种技能可以调用，能够高效完成复杂请求。
无论是病害检测、知识查询、防治建议，还是对话记忆，你都能处理。

初始工作目录：{directory}

根据用户需求，主动选择最合适的技能或技能组合。
对于复杂任务，可以分解问题并逐步使用不同技能解决。
使用每个技能后，清楚地解释执行结果并建议下一步操作。

如果需要停止交互，使用 `terminate` 工具调用。
"""
```

---

### 4. ❌ browser.py - 不适用

**用途：** 浏览器自动化任务

**可复用性：** 不适用

**原因：**
- 你的系统不涉及浏览器操作
- 专注于图片检测和知识查询

---

### 5. ❌ mcp.py - 不适用

**用途：** Model Context Protocol 服务器交互

**可复用性：** 不适用

**原因：**
- 你的系统使用 Skill 架构，不是 MCP
- 但可以参考其错误处理思路

---

### 6. ❌ swe.py - 不适用

**用途：** 软件工程/代码编辑任务

**可复用性：** 不适用

**原因：**
- 你的系统不涉及代码编辑
- 专注于农业领域应用

---

### 7. ⚠️ visualization.py - 可参考

**用途：** 数据分析和可视化任务

**可复用性：** 可参考思路

**复用价值：** ⭐⭐

**原因：**
- 强调工作目录管理
- 强调生成分析报告
- 可以借鉴到病害分析报告生成

**建议修改：**
```python
# 适配版本（如果需要添加报告生成功能）
DISEASE_ANALYSIS_REPORT_PROMPT = """
你是水稻病害分析专家，负责数据分析和报告生成任务。

注意事项：
1. 工作目录：{directory}；在工作目录中读写文件
2. 分析检测结果，提取关键信息
3. 最后生成病害分析结论报告

根据用户需求，逐步分解问题并使用不同技能解决。
注意：
1. 每步只选择一个最合适的技能
2. 使用技能后，清楚解释执行结果并建议下一步
3. 遇到错误时，审查并修复
"""
```

---

## 复用优先级总结

### 🔥 高优先级（强烈推荐）

1. **planning.py** → PlanningSkillAgent
   - 直接提升规划能力
   - 改进任务分解逻辑
   - 增强进度跟踪

2. **toolcall.py** → ToolExecutionAgent
   - 规范工具调用流程
   - 明确执行规则

### 🌟 中优先级（建议参考）

3. **manus.py** → ResponseSkillAgent 或系统级提示
   - 改进用户交互体验
   - 增强任务分解能力

4. **visualization.py** → 新增报告生成功能
   - 如果需要生成病害分析报告
   - 可以参考其结构

### ❄️ 低优先级（暂不需要）

5. **browser.py** - 不适用
6. **mcp.py** - 不适用
7. **swe.py** - 不适用

---

## 实施建议

### 第一阶段：核心提示词优化

1. **更新 PlanningSkillAgent**
   - 使用 planning.py 的结构化规划思路
   - 增强任务分解能力
   - 添加进度跟踪机制

2. **更新 ToolExecutionAgent**
   - 使用 toolcall.py 的简洁指导
   - 规范工具调用流程
   - 明确重试机制

### 第二阶段：体验优化

3. **更新 ResponseSkillAgent**
   - 参考 manus.py 的友好表达
   - 改进结果解释
   - 增强下一步建议

### 第三阶段：功能扩展（可选）

4. **添加报告生成功能**
   - 参考 visualization.py
   - 生成病害分析报告
   - 支持导出功能

---

## 具体实施步骤

### 步骤 1：创建新的提示词文件

创建 `prompts/rice_disease_prompts.py`：

```python
# -*- coding: utf-8 -*-
"""
水稻病害检测系统提示词
基于 OpenManus 提示词优化
"""

# 规划 Agent 提示词（基于 planning.py）
PLANNING_SYSTEM_PROMPT = """
你是水稻病害检测系统的规划专家，负责高效地制定结构化计划。

你的职责：
1. 分析用户请求，理解任务范围（病害检测、知识查询、防治建议等）
2. 创建清晰可执行的计划，选择合适的技能
3. 根据需要执行计划步骤
4. 跟踪进度并在必要时调整计划
5. 任务完成后立即结束

可用技能：
- DetectionSkill: 图片病害检测
- KnowledgeSkill: 农业知识查询和病害分析
- MemorySkill: 对话历史管理

将任务分解为逻辑步骤，考虑依赖关系。
知道何时结束 - 目标达成后不要继续思考。
"""

PLANNING_NEXT_STEP_PROMPT = """
基于当前状态，下一步行动是什么？
选择最高效的前进路径：
1. 计划是否充分，还是需要完善？
2. 能否立即执行下一步？
3. 任务是否完成？如果是，立即使用 `finish`。

简洁推理，然后选择合适的工具或行动。
"""

# 工具执行 Agent 提示词（基于 toolcall.py）
TOOL_EXECUTION_PROMPT = """
你是工具执行专家，负责调用各种技能完成任务。

可用技能：
- DetectionSkill.detect_objects: 检测图片中的病害
- KnowledgeSkill.query_knowledge: 查询农业知识
- KnowledgeSkill.analyze_detection: 分析检测结果
- MemorySkill.save_context: 保存对话上下文
- MemorySkill.get_recent_context: 获取最近对话

执行规则：
1. 根据计划选择合适的技能和能力
2. 提供正确格式的参数
3. 观察执行结果并判断是否成功
4. 最多重试2次
5. 如果需要停止交互，使用 `terminate` 工具调用
"""

# 系统级提示词（基于 manus.py）
SYSTEM_PROMPT = """
你是水稻病害智能助手，专注于解决用户提出的水稻病害相关任务。
你拥有多种技能可以调用，能够高效完成复杂请求。

初始工作目录：{directory}

根据用户需求，主动选择最合适的技能或技能组合。
对于复杂任务，可以分解问题并逐步使用不同技能解决。
使用每个技能后，清楚地解释执行结果并建议下一步操作。
"""

# 响应生成提示词
RESPONSE_GENERATION_PROMPT = """
你是响应生成专家，负责生成友好、有用的回复。

生成规则：
1. 使用清晰、专业的语言
2. 提供具体、可操作的建议
3. 包含病害特征和防治方法
4. 适当使用表情符号增强可读性
5. 根据情感调整语气（紧急、积极、消极）
"""
```

### 步骤 2：更新现有 Agent

修改 `services/agents_v3_impl_part3.py` 中的 PlanningSkillAgent：

```python
from prompts.rice_disease_prompts import PLANNING_SYSTEM_PROMPT, PLANNING_NEXT_STEP_PROMPT

class PlanningSkillAgent(PlanAgent):
    def __init__(self, llm=None, skill_client=None):
        super().__init__("PlanningAgent", llm)
        self.skill_client = skill_client
        self.system_prompt = PLANNING_SYSTEM_PROMPT  # 使用新提示词
```

### 步骤 3：测试和验证

创建测试脚本验证新提示词的效果。

---

## 预期改进效果

### 1. 规划能力提升
- 更清晰的任务分解
- 更好的进度跟踪
- 更准确的完成判断

### 2. 执行效率提升
- 更规范的工具调用
- 更好的错误处理
- 更明确的重试机制

### 3. 用户体验提升
- 更友好的交互
- 更清晰的结果解释
- 更有用的下一步建议

---

## 总结

**可以直接复用的提示词：**
1. ✅ planning.py - 用于 PlanningSkillAgent
2. ✅ toolcall.py - 用于 ToolExecutionAgent

**可以参考的提示词：**
3. ⚠️ manus.py - 用于系统级提示或 ResponseSkillAgent
4. ⚠️ visualization.py - 如果需要报告生成功能

**不适用的提示词：**
5. ❌ browser.py - 浏览器自动化
6. ❌ mcp.py - MCP 协议
7. ❌ swe.py - 代码编辑

建议优先实施 planning.py 和 toolcall.py 的复用，这两个可以立即提升系统的规划和执行能力。
