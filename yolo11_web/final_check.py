# -*- coding: utf-8 -*-
# Simpler dependency check
f = open('dep_check.txt', 'w', encoding='utf-8')
f.write('=== Dependency Check ===\n')

# Core deps
core_deps = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'uvicorn'),
    ('pydantic', 'pydantic'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('redis', 'redis'),
    ('langchain', 'langchain'),
    ('langchain_core', 'langchain-core'),
    ('langgraph', 'langgraph'),
    ('loguru', 'loguru'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
]

for mod, name in core_deps:
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', 'unknown')
        f.write(f'[OK] {name}: {ver}\n')
    except ImportError:
        f.write(f'[MISSING] {name}\n')
    except Exception as e:
        f.write(f'[ERROR] {name}: {str(e)[:30]}\n')

f.write('\nDone\n')
f.close()