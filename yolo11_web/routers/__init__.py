# -*- coding: utf-8 -*-
"""
路由模块
"""

from fastapi import APIRouter
from routers import users, news, favorite, history, mcp_agent, langgraph_api, detection, export

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(users.router)
api_router.include_router(news.router)
api_router.include_router(favorite.router)
api_router.include_router(history.router)
api_router.include_router(mcp_agent.router)  # 新的MCP智能助手路由
api_router.include_router(langgraph_api.router)  # LangGraph API 路由
api_router.include_router(detection.router)  # 病害检测API
# api_router.include_router(monitoring.router)  # 系统监控API (已禁用)
api_router.include_router(export.router)  # 导出API

__all__ = ["api_router"]
