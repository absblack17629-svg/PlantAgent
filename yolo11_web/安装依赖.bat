@echo off
chcp 65001 >nul
echo ============================================================
echo YOLO11 智能体系统 - 依赖安装脚本
echo ============================================================
echo.

echo [1/3] 升级 pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ pip 升级失败
    pause
    exit /b 1
)
echo ✅ pip 升级成功
echo.

echo [2/3] 安装所有依赖（不指定版本，自动解决冲突）...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    echo.
    echo 尝试使用 --upgrade 参数重新安装...
    pip install -r requirements.txt --upgrade
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装仍然失败
        pause
        exit /b 1
    )
)
echo ✅ 依赖安装成功
echo.

echo [3/3] 验证核心依赖...
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)"
python -c "import torch; print('✅ PyTorch:', torch.__version__)"
python -c "import ultralytics; print('✅ Ultralytics:', ultralytics.__version__)"
python -c "import langchain; print('✅ LangChain:', langchain.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import redis; print('✅ Redis:', redis.__version__)"
python -c "import psutil; print('✅ psutil:', psutil.__version__)"
echo.

echo ============================================================
echo 安装完成！
echo ============================================================
echo.
echo 下一步:
echo 1. 配置 .env 文件
echo 2. 初始化数据库: python init_database.py
echo 3. 启动服务: python main.py
echo.
pause
