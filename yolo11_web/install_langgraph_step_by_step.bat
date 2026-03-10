@echo off
echo ========================================
echo 按依赖顺序安装 LangGraph 相关包
echo ========================================

echo.
echo [1/6] 安装基础依赖...
pip install typing-extensions pydantic annotated-types

echo.
echo [2/6] 安装 JSON Schema...
pip install jsonschema jsonschema-specifications

echo.
echo [3/6] 安装 LangChain 核心...
pip install langchain-core==0.1.52

echo.
echo [4/6] 安装 LangChain 文本分割器...
pip install langchain-text-splitters

echo.
echo [5/6] 安装 LangGraph...
pip install langgraph==0.0.55

echo.
echo [6/6] 安装 LangGraph Checkpoint...
pip install langgraph-checkpoint==1.0.4

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
