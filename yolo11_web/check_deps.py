# -*- coding: utf-8 -*-
"""Check dependencies"""
import sys

modules = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'uvicorn'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('redis', 'redis'),
    ('langchain', 'langchain'),
    ('langgraph', 'langgraph'),
    ('langchain_core', 'langchain-core'),
    ('langchain_community', 'langchain-community'),
    ('ultralytics', 'YOLO'),
    ('torch', 'torch'),
    ('faiss', 'faiss'),
    ('sentence_transformers', 'sentence_transformers'),
    ('pydantic', 'pydantic'),
    ('loguru', 'loguru'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
]

print("=" * 50)
print("Dependency Check")
print("=" * 50)

missing = []
for module, name in modules:
    try:
        __import__(module)
        print(f"[OK] {name}")
    except ImportError as e:
        print(f"[MISSING] {name}: {e}")
        missing.append(name)

print("=" * 50)
if missing:
    print(f"Missing: {', '.join(missing)}")
else:
    print("All dependencies OK!")
print("=" * 50)