# -*- coding: utf-8 -*-
"""
FastAPI应用入口
YOLO11智能体系统 - 异步版本
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings, init_db, init_redis, close_redis
from routers import api_router
from utils.logger import get_logger
from utils.exceptions import (
    BusinessException,
    business_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


# 1. 简单的UTF-8编码设置（解决Windows上的GBK编码错误）
def setup_utf8_encoding():
    """
    简单的UTF-8编码设置，避免复杂的重写操作
    """
    # 设置环境变量（最有效的方法）
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

    # Windows系统特定设置
    if sys.platform == "win32":
        try:
            # 使用简单的reconfigure方法
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except:
            # 如果reconfigure失败，使用更简单的方法
            try:
                import io

                # 只在需要时创建新的wrapper
                if isinstance(sys.stdout, io.TextIOWrapper):
                    sys.stdout = io.TextIOWrapper(
                        sys.stdout.buffer,
                        encoding="utf-8",
                        errors="replace",
                        write_through=True,
                    )
                if isinstance(sys.stderr, io.TextIOWrapper):
                    sys.stderr = io.TextIOWrapper(
                        sys.stderr.buffer,
                        encoding="utf-8",
                        errors="replace",
                        write_through=True,
                    )
            except:
                # 如果所有方法都失败，只设置环境变量
                pass

    # 设置日志避免emoji问题
    import builtins

    original_print = builtins.print

    def safe_print(*args, **kwargs):
        """安全的print函数，完全避免emoji"""
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # 完全避免使用emoji，使用纯文本
                arg = (
                    arg.replace("[ROCKET]", "[启动]")
                    .replace("[OK]", "[成功]")
                    .replace("[WARN]", "[警告]")
                    .replace("[INFO]", "[提示]")
                    .replace("[STOP]", "[停止]")
                    .replace("[Node 5]", "[搜索]")
                    .replace("[FAIL]", "[错误]")
                    .replace("[STATS]", "[图表]")
                    .replace("[CROP]", "[水稻]")
                    .replace("[DETECT]", "[显微镜]")
                )
            safe_args.append(arg)
        return original_print(*safe_args, **kwargs)

    builtins.print = safe_print
    print("[INFO] UTF-8编码设置完成")


# 应用编码设置
setup_utf8_encoding()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("[启动] 启动YOLO11智能体系统...")

    # 创建必要的目录
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.RESULT_FOLDER, exist_ok=True)

    # 初始化数据库
    try:
        await init_db()
        logger.info("[成功] 数据库初始化成功")
    except Exception as e:
        logger.warning(f"[警告] 数据库初始化失败: {e}")
        logger.info("[提示] 应用将在无数据库模式下运行")

    # 初始化Redis
    try:
        await init_redis()
        logger.info("[成功] Redis初始化成功")
    except Exception as e:
        logger.warning(f"[警告] Redis初始化失败: {e}")
        logger.info("[提示] 应用将在无Redis模式下运行")

    logger.info(f"[成功] 服务启动成功: http://{settings.HOST}:{settings.PORT}")

    yield

    # 关闭时执行
    logger.info("[停止] 关闭YOLO11智能体系统...")
    await close_redis()
    logger.info("[成功] 服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于FastAPI的YOLO11智能体系统",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(api_router)


@app.get("/info")
async def langgraph_info():
    """LangGraph 服务器信息端点（用于前端连接检查）"""
    return {
        "version": "1.0.0",
        "status": "ok",
        "server": "YOLO11 LangGraph API",
        "assistants": ["agent"],
    }


@app.get("/")
async def root():
    """根路径 - 返回首页（农业资讯）"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    # 读取HTML文件 - 使用新的 index.html
    html_path = Path("templates/index.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    # 如果文件不存在，返回JSON
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/login")
async def login_page():
    """登录页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/login.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "登录页面未找到"}


@app.get("/register")
async def register_page():
    """注册页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/register.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "注册页面未找到"}


@app.get("/news/{news_id}")
async def news_detail_page(news_id: int):
    """新闻详情页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/news_detail.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "新闻详情页面未找到"}


@app.get("/news")
async def news_page():
    """农业资讯页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/index.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "资讯页面未找到"}


@app.get("/agent")
async def agent_page():
    """智能助手页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    # 尝试查找 agent.html，如果不存在则使用 index.html
    html_path = Path("templates/agent.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    # 如果没有专门的 agent.html，复制 index.html 的内容
    html_path = Path("templates/index.html")
    if html_path.exists():
        content = html_path.read_text(encoding="utf-8")
        # 简单替换标题
        content = content.replace("水稻病害智能识别系统", "智能助手")
        return HTMLResponse(content=content)

    return {"msg": "智能助手页面未找到"}


@app.get("/profile")
async def profile_page():
    """个人中心页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/profile.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "个人中心页面未找到"}


@app.get("/favorites")
async def favorites_page():
    """收藏列表页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/favorites.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "收藏列表页面未找到"}


@app.get("/user/history")
async def user_history_page():
    """用户历史记录页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("templates/user_history.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "历史记录页面未找到"}


@app.get("/test_auth")
async def test_auth_page():
    """认证测试页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("test_auth.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "测试页面未找到"}


@app.get("/test_history")
async def test_history_page():
    """历史记录测试页面"""
    from fastapi.responses import HTMLResponse
    from pathlib import Path

    html_path = Path("test_history.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    return {"msg": "测试页面未找到"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
