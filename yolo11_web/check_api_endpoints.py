#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查API端点
"""

import requests
import sys
import json


def check_all_endpoints():
    """检查所有API端点"""
    base_url = "http://localhost:8000"

    print("=== 检查后端API端点 ===")

    # 检查根路径
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"GET / - 状态: {response.status_code}")
    except:
        print(f"GET / - 服务器未运行")
        return False

    # 检查docs
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"GET /docs - 状态: {response.status_code}")
    except:
        print(f"GET /docs - 不可用")

    # 检查API路由前缀
    print("\n=== 检查API路由 ===")

    # 可能的检测API端点
    endpoints = [
        ("/api/detect", "直接检测"),
        ("/api/detection/detect", "检测API"),
        ("/api/agent/mcp/process", "MCP处理"),
        ("/api/langgraph/process", "LangGraph处理"),
    ]

    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"GET {endpoint} ({name}) - 状态: {response.status_code}")
        except Exception as e:
            print(f"GET {endpoint} ({name}) - 错误: {type(e).__name__}")

    # 检查OpenAPI schema
    print("\n=== 检查OpenAPI Schema ===")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            schema = response.json()
            # 提取所有路径
            paths = list(schema.get("paths", {}).keys())
            print(f"可用的API路径 ({len(paths)} 个):")
            for path in sorted(paths):
                print(f"  {path}")
            return True
        else:
            print(f"OpenAPI schema不可用: {response.status_code}")
            return False
    except Exception as e:
        print(f"无法获取OpenAPI schema: {e}")
        return False


def check_detection_endpoint():
    """检查检测API的具体端点"""
    base_url = "http://localhost:8000"

    print("\n=== 测试检测API端点 ===")

    # 尝试POST请求
    endpoints = [
        ("/api/detection/detect", "检测路由"),
        ("/api/detect", "直接检测"),
    ]

    for endpoint, name in endpoints:
        print(f"\n测试: {name} ({endpoint})")

        # 准备测试数据
        data = {"image_path": "bus.jpg", "user_question": "检测这张图片中的病害"}

        files = None
        try:
            with open("bus.jpg", "rb") as f:
                files = {"file": ("bus.jpg", f, "image/jpeg")}
                response = requests.post(
                    f"{base_url}{endpoint}", files=files, timeout=10
                )
                print(f"  POST {endpoint} - 状态: {response.status_code}")
                if response.status_code != 200:
                    print(f"  错误响应: {response.text[:200]}")
                else:
                    print(f"  成功: {response.json()}")
                    return True
        except FileNotFoundError:
            print(f"  测试图片不存在")
        except Exception as e:
            print(f"  POST请求失败: {type(e).__name__}: {e}")

    return False


if __name__ == "__main__":
    # 检查所有端点
    if check_all_endpoints():
        print("\n[OK] 后端服务器正常")
    else:
        print("\n[ERROR] 后端服务器有问题")

    # 检查检测端点
    if check_detection_endpoint():
        print("\n检测API端点可用")
    else:
        print("\n检测API端点有问题")

    print("\n=== 建议 ===")
    print("1. 检查前端是否运行: npm run dev")
    print("2. 检查前端调用API的URL是否正确")
    print("3. 在浏览器开发者工具Network标签中查看请求")
