# -*- coding: utf-8 -*-
"""
测试检测功能修复
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_detection_service():
    """测试检测服务"""
    print("测试检测服务...")
    try:
        from services.detection_service import get_detection_service

        detection_service = get_detection_service()
        print(f"检测服务已加载: {detection_service is not None}")

        # 测试检测
        test_image = "static/uploads/20260310_150832_71f62774.jpg"
        if os.path.exists(test_image):
            print(f"测试图片存在: {test_image}")
            result = await detection_service.detect_objects(test_image)
            print(f"检测结果: {result}")
        else:
            print(f"测试图片不存在: {test_image}")

    except Exception as e:
        print(f"测试检测服务失败: {e}")
        import traceback

        traceback.print_exc()


async def test_langchain_tool():
    """测试LangChain工具"""
    print("\n测试LangChain工具...")
    try:
        from yoloapp.tool.langchain_tools import detect_rice_disease

        test_image = "static/uploads/20260310_150832_71f62774.jpg"
        if os.path.exists(test_image):
            result = await detect_rice_disease(test_image)
            print(f"LangChain工具检测结果: {result}")
        else:
            print(f"测试图片不存在: {test_image}")

    except Exception as e:
        print(f"测试LangChain工具失败: {e}")
        import traceback

        traceback.print_exc()


async def test_nine_node_workflow():
    """测试九节点工作流"""
    print("\n测试九节点工作流...")
    try:
        from yoloapp.flow.nine_node_with_tools import run_nine_node_workflow

        test_image = "static/uploads/20260310_150832_71f62774.jpg"
        if os.path.exists(test_image):
            result = await run_nine_node_workflow("检测这张图片", test_image)
            print(f"工作流结果: {result}")
            print(f"是否包含tools_used字段: {'tools_used' in result}")
            if "tools_used" in result:
                print(f"tools_used值: {result['tools_used']}")
        else:
            print(f"测试图片不存在: {test_image}")

    except Exception as e:
        print(f"测试九节点工作流失败: {e}")
        import traceback

        traceback.print_exc()


async def test_api_endpoint():
    """测试API端点"""
    print("\n模拟API调用...")
    try:
        import requests

        test_image = "static/uploads/20260310_150832_71f62774.jpg"
        if os.path.exists(test_image):
            # 模拟API调用
            url = "http://localhost:8000/api/agent/chat"
            files = {"image": open(test_image, "rb")}
            data = {"message": "检测这张图片"}

            response = requests.post(url, files=files, data=data)
            print(f"API响应状态码: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"API响应: {result}")
                if result.get("code") == 200:
                    print(
                        f"是否包含tools_used字段: {'tools_used' in result.get('data', {})}"
                    )
                    if "tools_used" in result.get("data", {}):
                        print(f"tools_used值: {result['data']['tools_used']}")
            else:
                print(f"API调用失败: {response.text}")
        else:
            print(f"测试图片不存在: {test_image}")

    except Exception as e:
        print(f"测试API端点失败: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试检测功能修复")
    print("=" * 60)

    # 测试检测服务
    await test_detection_service()

    # 测试LangChain工具
    await test_langchain_tool()

    # 测试九节点工作流
    await test_nine_node_workflow()

    # 测试API端点（需要服务器运行）
    # await test_api_endpoint()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
