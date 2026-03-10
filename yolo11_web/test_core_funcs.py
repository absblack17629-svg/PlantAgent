# -*- coding: utf-8 -*-
"""核心功能测试脚本"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

results = []

def test(name, func):
    try:
        func()
        results.append((name, True, ""))
    except Exception as e:
        results.append((name, False, str(e)))

# 1. Schema模块
def test_schema():
    from yoloapp.schema import AgentRole, AgentState, Message, Memory, ToolResult
    msg = Message.user_message("test")
    assert msg.role == "user"
test("Schema模块", test_schema)

# 2. Exception模块
def test_exceptions():
    from yoloapp.exceptions import AgentError, DetectionError, RAGError, LLMError
    e = AgentError("test error")
    assert e.message == "test error"
test("Exception模块", test_exceptions)

# 3. Config模块
def test_config():
    from yoloapp.config import get_config_manager
    cfg = get_config_manager()
    assert cfg is not None
test("Config模块", test_config)

# 4. LLM模块
def test_llm():
    from yoloapp.llm import get_llm_client
    client = get_llm_client("default")
    assert client is not None
test("LLM客户端", test_llm)

# 5. RAG模块
def test_rag():
    from yoloapp.rag import get_rag_service
    rag = get_rag_service()
    assert rag is not None
test("RAG服务", test_rag)

# 6. Agent模块
def test_agent():
    from yoloapp.agent import BaseAgent, IntentAgent, NineNodeOrchestrator
    orch = NineNodeOrchestrator()
    assert orch is not None
test("Agent系统", test_agent)

# 7. Flow模块
def test_flow():
    from yoloapp.flow.base import BaseFlow
    assert BaseFlow is not None
test("Flow编排", test_flow)

# 8. Tool模块
def test_tools():
    from yoloapp.tool import BaseTool, MemoryTool
    assert BaseTool is not None
    assert MemoryTool is not None
test("Tool工具", test_tools)

# 9. Utils模块
def test_utils():
    from yoloapp.utils.logger import get_logger
    logger = get_logger(__name__)
    assert logger is not None
test("日志工具", test_utils)

# 10. FastAPI导入
def test_fastapi():
    import fastapi
    import uvicorn
test("FastAPI框架", test_fastapi)

# 11. YOLO导入
def test_yolo():
    from ultralytics import YOLO
test("YOLO模型", test_yolo)

# 12. 数据库
def test_db():
    from sqlalchemy import create_engine
test("SQLAlchemy", test_db)

# 13. Redis
def test_redis():
    import redis
test("Redis客户端", test_redis)

# 14. LangChain
def test_langchain():
    from langchain_core.messages import HumanMessage
test("LangChain", test_langchain)

# 15. 向量数据库
def test_faiss():
    import faiss
test("FAISS向量库", test_faiss)

# 打印结果
passed = 0
failed = 0
print("\n" + "="*50)
print("核心功能测试报告")
print("="*50)
for name, ok, error in results:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}")
    if not ok:
        print(f"      错误: {error}")
    if ok:
        passed += 1
    else:
        failed += 1

print("="*50)
print(f"通过: {passed}/{len(results)}")
print(f"失败: {failed}/{len(results)}")
print("="*50)

sys.exit(0 if failed == 0 else 1)