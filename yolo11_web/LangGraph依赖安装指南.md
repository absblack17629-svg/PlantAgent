# LangGraph 依赖安装指南

## 依赖关系图

```
langgraph (0.0.55)
├── langchain-core (0.1.52)
│   ├── pydantic (>=1.10.0)
│   ├── typing-extensions (>=4.0.0)
│   ├── jsonpatch (>=1.33)
│   └── jsonschema (>=4.0.0)
├── langgraph-checkpoint (1.0.4)
└── langchain-text-splitters
```

## 安装方法

### 方法 1：分步安装（推荐）

```bash
install_langgraph_step_by_step.bat
```

这个脚本会按依赖顺序安装：
1. 基础依赖（typing-extensions, pydantic）
2. JSON 相关（jsonschema, jsonpatch）
3. langchain-core
4. langchain-text-splitters
5. langgraph
6. langgraph-checkpoint

### 方法 2：最小化安装（有冲突时）

```bash
install_langgraph_minimal.bat
```

这个脚本会：
1. 先安装核心包（不检查依赖）
2. 然后让 pip 自动解决依赖
3. 修复缺失的依赖

### 方法 3：手动安装

如果脚本都失败，手动执行：

```bash
# 1. 安装核心
pip install langchain-core==0.1.52

# 2. 安装 LangGraph
pip install langgraph==0.0.55

# 3. 验证
python -c "import langgraph; print('OK')"
```

## 常见问题

### Q1: 版本冲突

**错误**: `ERROR: pip's dependency resolver does not currently take into account all the packages that are installed...`

**解决**:
```bash
# 方案 A: 忽略依赖检查
pip install langgraph --no-deps
pip install langchain-core --no-deps
pip check  # 查看缺失的依赖
pip install <缺失的包>

# 方案 B: 使用虚拟环境
python -m venv venv_langgraph
venv_langgraph\Scripts\activate
pip install langgraph==0.0.55
```

### Q2: 已安装的包版本不兼容

**错误**: `Requirement already satisfied: langchain-core==0.2.x but you have 0.1.52`

**解决**:
```bash
# 强制重装
pip install langchain-core==0.1.52 --force-reinstall --no-deps
pip install langgraph==0.0.55 --force-reinstall --no-deps
```

### Q3: 缺少 C++ 编译器

**错误**: `error: Microsoft Visual C++ 14.0 or greater is required`

**解决**:
1. 下载安装 Visual Studio Build Tools
2. 或使用预编译的 wheel: `pip install <package> --only-binary :all:`

## 验证安装

运行验证脚本：

```bash
python -c "import langgraph; print('langgraph:', langgraph.__version__)"
python -c "import langchain_core; print('langchain_core:', langchain_core.__version__)"
python -c "from langgraph.graph import StateGraph; print('StateGraph OK')"
```

预期输出：
```
langgraph: 0.0.55
langchain_core: 0.1.52
StateGraph OK
```

## 完整依赖列表

如果需要从零开始安装所有依赖：

```bash
# 基础
pip install typing-extensions>=4.0.0
pip install pydantic>=1.10.0
pip install annotated-types

# JSON
pip install jsonschema>=4.0.0
pip install jsonschema-specifications
pip install jsonpatch>=1.33

# LangChain
pip install langchain-core==0.1.52
pip install langchain-text-splitters

# LangGraph
pip install langgraph==0.0.55
pip install langgraph-checkpoint==1.0.4
```

## 最小可用版本

如果你的环境有严格的版本限制，这些是最小可用版本：

```
langchain-core>=0.1.0
langgraph>=0.0.50
pydantic>=1.10.0
typing-extensions>=4.0.0
```

## 回退方案

如果实在无法安装 LangGraph，系统已经配置了自动回退：

1. 后端会自动检测 LangGraph 是否可用
2. 如果不可用，会使用旧的 `NineNodeOrchestrator`
3. 功能完全相同，只是不使用 LangGraph 的状态图

查看回退日志：
```
logger.warning("LangGraph 未安装，回退到旧的 Orchestrator")
```

## 下一步

安装完成后：

1. 重启后端: `python main.py`
2. 运行测试: `python test_simple_agent.py`
3. 运行诊断: `python diagnose_frontend_backend.py`

如果测试通过，前端就可以正常使用了！
