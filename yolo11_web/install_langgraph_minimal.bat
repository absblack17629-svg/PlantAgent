@echo off
echo ========================================
echo 最小化安装 LangGraph（避免冲突）
echo ========================================

echo.
echo 这个脚本会尝试安装最小依赖集
echo 如果遇到冲突，会跳过已安装的包
echo.
pause

echo.
echo [1/4] 安装 LangChain Core（允许已存在）...
pip install langchain-core --upgrade --no-deps
pip install langchain-core

echo.
echo [2/4] 安装 LangGraph（允许已存在）...
pip install langgraph --no-deps
pip install langgraph

echo.
echo [3/4] 修复可能缺失的依赖...
pip install jsonpatch

echo.
echo [4/4] 验证安装...
python -c "import langgraph; print('✅ langgraph 已安装')" 2>nul || echo ❌ langgraph 安装失败
python -c "import langchain_core; print('✅ langchain_core 已安装')" 2>nul || echo ❌ langchain_core 安装失败

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 如果仍有问题，请查看具体错误信息
echo 或者尝试: pip install langgraph --force-reinstall
echo.
pause
