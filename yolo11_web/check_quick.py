# -*- coding: utf-8 -*-
"""Quick dependency check"""
import sys

results = []

def check(mod, name):
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', 'unknown')
        results.append(f'OK: {name} ({ver})')
    except ImportError:
        results.append(f'MISSING: {name}')
    except Exception as e:
        results.append(f'ERROR: {name} - {str(e)[:50]}')

# Quick check (skip slow ones)
deps = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'uvicorn'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('redis', 'redis'),
    ('langchain', 'langchain'),
    ('langchain_core', 'langchain-core'),
    ('langgraph', 'langgraph'),
    ('pydantic', 'pydantic'),
    ('loguru', 'loguru'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
    ('ultralytics', 'ultralytics'),
    ('torch', 'torch'),
    ('numpy', 'numpy'),
    ('requests', 'requests'),
    ('passlib', 'passlib'),
    ('jose', 'python-jose'),
    ('tenacity', 'tenacity'),
    ('dotenv', 'python-dotenv'),
    ('email_validator', 'email-validator'),
    ('pydantic_settings', 'pydantic-settings'),
    ('apscheduler', 'APScheduler'),
]

for mod, name in deps:
    check(mod, name)

# Write to file
with open('dep_result.txt', 'w', encoding='utf-8') as f:
    for r in results:
        f.write(r + '\n')
    
    missing = [r for r in results if 'MISSING' in r]
    errors = [r for r in results if 'ERROR' in r]
    
    f.write(f'\nTotal: {len(results)}, Missing: {len(missing)}, Errors: {len(errors)}\n')
    if missing:
        f.write(f'MISSING: {", ".join([r.split(": ")[1] for r in missing])}\n')

print("Done")