@echo off
echo ========================================
echo 使用 Python 直接安装 LangGraph
echo ========================================

echo.
echo [1/6] 安装基础依赖...
python -m pip install typing-extensions pydantic annotated-types

echo.
echo [2/6] 安装 JSON Schema...
python -m pip install jsonschema jsonschema-specifications

echo.
echo [3/6] 安装 LangChain 核心...
python -m pip install langchain-core==0.1.52

echo.
echo [4/6] 安装 LangChain 文本分割器...
python -m pip install langchain-text-splitters

echo.
echo [5/6] 安装 LangGraph...
python -m pip install langgraph==0.0.55

echo.
echo [6/6] 安装 LangGraph Checkpoint...
python -m pip install langgraph-checkpoint==1.0.4

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 验证安装:
python -c "import langgraph; print('✅ langgraph:', langgraph.__version__)"
python -c "import langchain_core; print('✅ langchain_core:', langchain_core.__version__)"

echo.
echo 现在可以重启后端:
echo   python main.py
echo.
pause
