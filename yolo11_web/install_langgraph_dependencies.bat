@echo off
echo ========================================
echo 安装 LangGraph 相关依赖
echo ========================================

echo.
echo 正在安装 LangGraph 核心包...
pip install langgraph==0.0.55
pip install langgraph-checkpoint==1.0.4

echo.
echo 正在安装 LangChain 核心包...
pip install langchain-core==0.1.52
pip install langchain-community==0.0.38
pip install langchain-text-splitters

echo.
echo 正在安装 OpenAI 客户端...
pip install openai

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 现在可以运行测试:
echo   python test_simple_agent.py
echo.
echo 或启动服务:
echo   python main.py
echo.
pause
