# -*- coding: utf-8 -*-
"""Comprehensive dependency check"""
import sys

results = []

def check(mod, name):
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', 'unknown')
        results.append(f'[OK] {name} ({ver})')
    except ImportError:
        results.append(f'[MISSING] {name}')
    except Exception as e:
        results.append(f'[ERROR] {name}: {e}')

# Check all dependencies
deps = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'uvicorn'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('redis', 'redis'),
    ('langchain', 'langchain'),
    ('langchain_core', 'langchain-core'),
    ('langchain_community', 'langchain-community'),
    ('langgraph', 'langgraph'),
    ('pydantic', 'pydantic'),
    ('loguru', 'loguru'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
    ('ultralytics', 'ultralytics'),
    ('torch', 'torch'),
    ('faiss', 'faiss'),
    ('sentence_transformers', 'sentence-transformers'),
    ('numpy', 'numpy'),
    ('PIL', 'Pillow'),
    ('cv2', 'opencv-python'),
    ('requests', 'requests'),
    ('passlib', 'passlib'),
    ('jose', 'python-jose'),
    ('tiktoken', 'tiktoken'),
    ('tenacity', 'tenacity'),
    ('dotenv', 'python-dotenv'),
    ('email_validator', 'email-validator'),
    ('pydantic_settings', 'pydantic-settings'),
]

for mod, name in deps:
    check(mod, name)

# Write to file
with open('dependency_check_result.txt', 'w', encoding='utf-8') as f:
    f.write('=' * 50 + '\n')
    f.write('Dependency Check Results\n')
    f.write('=' * 50 + '\n\n')
    for r in results:
        f.write(r + '\n')
    
    # Summary
    missing = [r for r in results if 'MISSING' in r]
    errors = [r for r in results if 'ERROR' in r]
    
    f.write('\n' + '=' * 50 + '\n')
    f.write(f'Summary: {len(results)} checked, {len(missing)} missing, {len(errors)} errors\n')
    f.write('=' * 50 + '\n')
    
    if missing:
        f.write('\nMISSING packages:\n')
        for m in missing:
            f.write(f'  {m}\n')
    
    if errors:
        f.write('\nERROR packages:\n')
        for e in errors:
            f.write(f'  {e}\n')

print("Results written to dependency_check_result.txt")