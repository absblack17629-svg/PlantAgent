@echo off
echo === Checking dependencies ===
pip show fastapi > nul 2>&1 && echo [OK] fastapi || echo [MISSING] fastapi
pip show uvicorn > nul 2>&1 && echo [OK] uvicorn || echo [MISSING] uvicorn
pip show langchain > nul 2>&1 && echo [OK] langchain || echo [MISSING] langchain
pip show langgraph > nul 2>&1 && echo [OK] langgraph || echo [MISSING] langgraph
pip show pydantic > nul 2>&1 && echo [OK] pydantic || echo [MISSING] pydantic
echo === Done ===