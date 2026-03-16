# -*- coding: utf-8 -*-
"""
FastAPI应用入口 - 简化版
跳过有问题的模块
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import config

app = FastAPI(
    title="水稻病害识别系统",
    version="2.0.0",
    description="基于YOLO11的水稻病害智能检测系统"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {
        "app": "水稻病害识别系统",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# 基础路由
@app.get("/api/info")
async def api_info():
    return {
        "name": "水稻病害识别API",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
