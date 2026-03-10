@echo off
echo ========================================
echo 清理旧进程并重启服务
echo ========================================
echo.

echo [1/3] 停止所有 Python 进程...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] 清理日志文件锁定...
timeout /t 1 /nobreak >nul

echo [3/3] 启动新服务...
echo.
echo 正在启动 YOLO-SGHM 智能体系统...
echo 预加载功能已启用，首次启动可能需要30-60秒
echo.
python main.py

pause
