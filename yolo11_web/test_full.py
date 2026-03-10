# -*- coding: utf-8 -*-
"""Complete functionality test"""
import sys
import os

os.chdir(r'C:\Users\1\Desktop\file\Fastapi_backend\yolo11_web')

f = open('full_test_result.txt', 'w', encoding='utf-8')

def log(msg):
    f.write(msg + '\n')
    print(msg)

log('='*50)
log('COMPLETE FUNCTIONALITY TEST')
log('='*50)

ok = 0
fail = 0

# === DEPENDENCIES ===
log('\n[DEPENDENCIES]')
deps = [
    'fastapi', 'uvicorn', 'sqlalchemy', 'redis', 'langchain',
    'langchain_core', 'langchain_community', 'langgraph', 'pydantic',
    'loguru', 'openpyxl', 'psutil', 'ultralytics', 'torch', 'faiss',
    'sentence_transformers', 'numpy', 'PIL', 'cv2', 'requests'
]
for dep in deps:
    try:
        __import__(dep)
        log(f'  [OK] {dep}')
        ok += 1
    except:
        log(f'  [FAIL] {dep}')
        fail += 1

# === CORE MODULES ===
log('\n[CORE MODULES]')
modules = [
    'yoloapp.schema', 'yoloapp.exceptions', 'yoloapp.config',
    'yoloapp.llm', 'yoloapp.rag', 'yoloapp.agent', 
    'yoloapp.tool', 'yoloapp.flow', 'yoloapp.utils'
]
for mod in modules:
    try:
        __import__(mod)
        log(f'  [OK] {mod}')
        ok += 1
    except Exception as e:
        log(f'  [FAIL] {mod}: {e}')
        fail += 1

# === YOLO MODEL ===
log('\n[YOLO MODEL]')
try:
    from ultralytics import YOLO
    model = YOLO('yolo11n.pt')
    log('  [OK] YOLO11 model loaded')
    ok += 1
except Exception as e:
    log(f'  [FAIL] YOLO: {e}')
    fail += 1

# === CONFIG ===
log('\n[CONFIG]')
try:
    from config.settings import get_settings
    s = get_settings()
    log(f'  [OK] Settings: {s.APP_NAME}')
    ok += 1
except Exception as e:
    log(f'  [FAIL] Config: {e}')
    fail += 1

# === LLM ===
log('\n[LLM CLIENT]')
try:
    from yoloapp.llm import get_llm_client
    client = get_llm_client("default")
    log(f'  [OK] LLM Client: {type(client).__name__}')
    ok += 1
except Exception as e:
    log(f'  [FAIL] LLM: {e}')
    fail += 1

# === RAG ===
log('\n[RAG SERVICE]')
try:
    from yoloapp.rag import get_rag_service
    rag = get_rag_service()
    log(f'  [OK] RAG Service: {type(rag).__name__}')
    ok += 1
except Exception as e:
    log(f'  [FAIL] RAG: {e}')
    fail += 1

# === AGENT ===
log('\n[AGENT SYSTEM]')
try:
    from yoloapp.agent import NineNodeOrchestrator
    orch = NineNodeOrchestrator()
    log(f'  [OK] Agent: {type(orch).__name__}')
    ok += 1
except Exception as e:
    log(f'  [FAIL] Agent: {e}')
    fail += 1

# === TOOLS ===
log('\n[TOOLS]')
try:
    from yoloapp.tool import (
        MemoryTool, PlantingPlanTool, 
        WeatherTool, IrrigationTool
    )
    log('  [OK] All tools importable')
    ok += 1
except Exception as e:
    log(f'  [FAIL] Tools: {e}')
    fail += 1

# === ROUTERS ===
log('\n[API ROUTERS]')
try:
    from routers import users, news, detection, agent_factory
    log('  [OK] All routers importable')
    ok += 1
except Exception as e:
    log(f'  [FAIL] Routers: {e}')
    fail += 1

# === SUMMARY ===
log('\n' + '='*50)
log(f'RESULT: {ok} PASSED, {fail} FAILED')
log('='*50)
f.close()

print('Test complete!')