# YOLOApp 迁移完成

## 迁移状态

✅ **代码迁移已完成！**

所有核心代码已从 `services/` 和 `schemas/` 迁移到 `yoloapp/`。

## 新的目录结构

```
yoloapp/
├── __init__.py          # 统一导出（延迟导入）
├── llm.py               # LLM 客户端
├── token_counter.py     # Token 计数器
├── exceptions.py        # 异常处理
├── config.py            # 配置管理
├── rag.py               # RAG 服务
├── schema.py            # 数据模型
├── agent/               # Agent 实现
├── tool/                # Tool 实现
├── flow/                # Flow 编排
├── prompt/              # 提示词模板
└── utils/               # 工具函数
    └── logger.py        # 日志管理
```

## 新的导入方式

### 推荐方式（函数式）

```python
# LLM 客户端
from yoloapp import get_llm_client
llm = get_llm_client("default")

# 配置管理
from yoloapp import get_config_manager
config = get_config_manager()

# RAG 服务
from yoloapp import get_rag_service
rag = get_rag_service()
```

### 直接导入类

```python
# LLM
from yoloapp.llm import LLMClient, get_llm_client
from yoloapp.token_counter import TokenCounter

# 异常
from yoloapp.exceptions import (
    AgentError,
    DetectionError,
    RAGError,
    LLMError,
    APIError,
)

# Schema
from yoloapp.schema import Message, Memory, AgentState

# RAG
from yoloapp.rag import RAGService

# 配置
from yoloapp.config import get_config_manager

# 日志
from yoloapp.utils.logger import get_logger
```

## 向后兼容

旧的导入路径仍然可用（通过代理），但会显示废弃警告：

```python
# ⚠️ 废弃但仍可用
from services.llm import get_llm_client  # 会显示警告
from schemas.message import Message       # 会显示警告
```

## 下一步操作

### 1. 安装缺失的依赖

```bash
pip install openai langchain-core langchain-text-splitters
```

或使用现有的安装脚本：
```bash
install_rag_dependencies.bat
```

### 2. 更新 API Key

编辑 `.env` 文件，设置有效的 API Key：
```bash
# 火山引擎
ZHIPU_API_KEY=your-volcengine-key
ZHIPU_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ZHIPU_MODEL=glm-4.7

# 或智谱 AI
ZHIPU_API_KEY=your-zhipu-key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPU_MODEL=glm-4-flash
```

### 3. 运行测试验证

```bash
python test_rag_direct.py
```

预期输出：
```
✅ RAG 服务初始化成功
✅ LLM 客户端初始化成功
✅ 获得回答
🎉 RAG 服务完全正常！
```

### 4. 更新现有代码

使用以下脚本批量更新导入：
```bash
python update_imports_to_yoloapp.py
```

### 5. 清理旧代码（可选）

测试通过后，可以删除旧的目录：
```bash
# 备份后删除
rm -rf services/llm
rm -rf services/exceptions.py
rm -rf schemas/message.py
# ... 等等
```

## 迁移的优势

### 1. 更清晰的结构
- 所有应用代码在一个目录下
- 扁平化的模块结构
- 更容易导航和理解

### 2. 更好的导入
- 更短的导入路径
- 统一的命名空间
- 避免循环依赖

### 3. 更易维护
- 代码集中管理
- 减少重复
- 更容易重构

### 4. 符合最佳实践
- 遵循 OpenManus 风格
- 模块化设计
- 清晰的职责分离

## 常见问题

### Q: 旧代码还能用吗？
A: 可以！我们保留了向后兼容层，旧的导入路径仍然有效，只是会显示废弃警告。

### Q: 什么时候删除旧代码？
A: 建议：
1. 先完成所有测试
2. 逐步更新现有代码
3. 3-6 个月后删除旧代码

### Q: 如何更新现有项目？
A: 
1. 使用 `update_imports_to_yoloapp.py` 脚本
2. 或手动更新导入语句
3. 运行测试确保一切正常

### Q: 遇到导入错误怎么办？
A: 
1. 检查是否安装了所有依赖
2. 确认 `yoloapp/` 目录结构完整
3. 查看错误信息，可能是循环依赖

## 技术细节

### 延迟导入

`yoloapp/__init__.py` 使用延迟导入避免循环依赖：

```python
def get_llm_client(config_name: str = "default"):
    from yoloapp.llm import get_llm_client as _get_llm_client
    return _get_llm_client(config_name)
```

### 动态属性

使用 `__getattr__` 实现按需导入：

```python
def __getattr__(name):
    if name == "LLMClient":
        from yoloapp.llm import LLMClient
        return LLMClient
    # ...
```

### 向后兼容

旧文件通过代理实现兼容：

```python
# services/llm/client.py
warnings.warn("已废弃，请使用 yoloapp.llm")
from yoloapp.llm import *
```

## 总结

✅ 代码迁移完成
✅ 目录结构清晰
✅ 导入路径统一
✅ 向后兼容保留
⚠️ 需要安装依赖
⚠️ 需要有效 API Key

完成上述步骤后，您将拥有一个清晰、现代、易维护的代码库！
