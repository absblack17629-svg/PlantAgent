@echo off
echo ========================================
echo 重启 YOLO-SGHM 服务器
echo ========================================
echo.

echo 正在查找并停止现有服务...
for /f "tokens=2" %%i in ('tasklist ^| findstr "python.exe"') do (
    echo 发现 Python 进程: %%i
    taskkill /PID %%i /F 2>nul
)

echo.
echo 等待进程完全关闭...
timeout /t 3 /nobreak >nul

echo.
echo 启动新服务...
echo 预加载: YOLO模型 + RAG服务 + LLM客户端 + LangGraph工作流
echo.
start "YOLO-SGHM Server" python main.py

echo.
echo ✅ 服务已在新窗口中启动
echo.
pause
