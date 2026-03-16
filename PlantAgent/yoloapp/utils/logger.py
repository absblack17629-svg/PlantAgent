# -*- coding: utf-8 -*-
"""
日志配置
企业级日志管理
"""

import logging
import sys
from pathlib import Path
from loguru import logger

# 延迟导入 settings 避免循环依赖
def _get_settings():
    from config.settings import settings
    return settings

# 日志目录
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# 移除默认处理器
logger.remove()

# 控制台输出
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",  # 默认 DEBUG，可以通过环境变量控制
    colorize=True
)

# 文件输出 - 所有日志
logger.add(
    LOG_DIR / "app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="00:00",  # 每天午夜轮转
    retention="30 days",  # 保留30天
    compression="zip",  # 压缩旧日志
    encoding="utf-8"
)

# 文件输出 - 错误日志
logger.add(
    LOG_DIR / "error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="00:00",
    retention="90 days",  # 错误日志保留更久
    compression="zip",
    encoding="utf-8"
)


def get_logger(name: str = None):
    """获取日志记录器"""
    if name:
        return logger.bind(name=name)
    return logger
