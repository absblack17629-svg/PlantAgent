# -*- coding: utf-8 -*-
"""Dependency and functionality test"""
import sys

f = open('test_result.txt', 'w', encoding='utf-8')

def test(name, func):
    try:
        func()
        f.write(f'[OK] {name}\n')
    except Exception as e:
        f.write(f'[FAIL] {name}: {e}\n')

# Dependencies
def dep(mod):
    return lambda: __import__(mod)

test('fastapi', dep('fastapi'))
test('uvicorn', dep('uvicorn'))
test('sqlalchemy', dep('sqlalchemy'))
test('redis', dep('redis'))
test('langchain', dep('langchain'))
test('langchain_core', dep('langchain_core'))
test('langchain_community', dep('langchain_community'))
test('langgraph', dep('langgraph'))
test('pydantic', dep('pydantic'))
test('loguru', dep('loguru'))
test('openpyxl', dep('openpyxl'))
test('psutil', dep('psutil'))
test('ultralytics', dep('ultralytics'))
test('torch', dep('torch'))
test('faiss', dep('faiss'))
test('sentence_transformers', dep('sentence_transformers'))
test('numpy', dep('numpy'))
test('PIL', dep('PIL'))
test('cv2', dep('cv2'))
test('requests', dep('requests'))
test('passlib', dep('passlib'))
test('jose', dep('jose'))
test('tiktoken', dep('tiktoken'))
test('tenacity', dep('tenacity'))
test('dotenv', dep('dotenv'))
test('email_validator', dep('email_validator'))
test('pydantic_settings', dep('pydantic_settings'))

# Core modules
test('yoloapp.schema', lambda: __import__('yoloapp.schema'))
test('yoloapp.exceptions', lambda: __import__('yoloapp.exceptions'))
test('yoloapp.config', lambda: __import__('yoloapp.config'))
test('yoloapp.llm', lambda: __import__('yoloapp.llm'))
test('yoloapp.rag', lambda: __import__('yoloapp.rag'))
test('yoloapp.agent', lambda: __import__('yoloapp.agent'))
test('yoloapp.tool', lambda: __import__('yoloapp.tool'))
test('yoloapp.flow', lambda: __import__('yoloapp.flow'))
test('yoloapp.utils', lambda: __import__('yoloapp.utils'))

f.close()
print('Done')