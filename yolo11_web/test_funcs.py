# -*- coding: utf-8 -*-
"""Core functionality test"""

import sys
import os

os.chdir(r"C:\Users\1\Desktop\file\Fastapi_backend\yolo11_web")

f = open("func_result.txt", "w", encoding="utf-8")
f.write("=== Core Functionality Test ===\n\n")

ok = 0
fail = 0

# 1. YOLO模型加载
f.write("[1] YOLO Model Loading\n")
try:
    from ultralytics import YOLO

    model = YOLO("yolo11n.pt")
    f.write("[OK] YOLO model loaded\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] YOLO: {e}\n")
    fail += 1

# 2. Config加载
f.write("\n[2] Configuration\n")
try:
    from yoloapp.config import get_config_manager

    cfg = get_config_manager()
    f.write(f"[OK] Config loaded, LLM provider: {cfg.llm.provider}\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] Config: {e}\n")
    fail += 1

# 3. LLM客户端
f.write("\n[3] LLM Client\n")
try:
    from yoloapp.llm import get_llm_client

    client = get_llm_client("default")
    f.write(f"[OK] LLM client: {type(client).__name__}\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] LLM: {e}\n")
    fail += 1

# 4. RAG服务
f.write("\n[4] RAG Service\n")
try:
    from yoloapp.rag import get_rag_service

    rag = get_rag_service()
    f.write(f"[OK] RAG service: {type(rag).__name__}\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] RAG: {e}\n")
    fail += 1

# 5. Agent创建
f.write("\n[5] Agent System\n")
try:
    from yoloapp.agent import NineNodeOrchestrator

    orch = NineNodeOrchestrator()
    f.write(f"[OK] Agent orchestrator: {type(orch).__name__}\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] Agent: {e}\n")
    fail += 1

# 6. Tools
f.write("\n[6] Tools\n")
try:
    from yoloapp.tool import MemoryTool, PlantingPlanTool, WeatherTool, IrrigationTool

    f.write("[OK] Tools: MemoryTool, PlantingPlanTool, WeatherTool, IrrigationTool\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] Tools: {e}\n")
    fail += 1

# 7. Schema验证
f.write("\n[7] Schema Validation\n")
try:
    from yoloapp.schema import Message, AgentState, ToolResult

    msg = Message.user_message("test")
    state = AgentState.IDLE
    result = ToolResult(output={"test": "ok"}, success=True)
    f.write(f"[OK] Schema validation working\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] Schema: {e}\n")
    fail += 1

# 8. Database
f.write("\n[8] Database Connection\n")
try:
    from config.database import engine

    f.write("[OK] Database engine created\n")
    ok += 1
except Exception as e:
    f.write(f"[WARN] Database: {e}\n")
    # Not a hard fail

# 9. Redis
f.write("\n[9] Redis Connection\n")
try:
    from config.redis_config import get_redis_client

    redis_client = get_redis_client()
    f.write("[OK] Redis client created\n")
    ok += 1
except Exception as e:
    f.write(f"[WARN] Redis: {e}\n")

# 10. Router导入
f.write("\n[10] API Routers\n")
try:
    from routers import users, news, detection, agent_factory

    f.write("[OK] All routers importable\n")
    ok += 1
except Exception as e:
    f.write(f"[FAIL] Routers: {e}\n")
    fail += 1

f.write(f"\n=== Summary: {ok} OK, {fail} Failed ===\n")
f.close()

print("Done")
