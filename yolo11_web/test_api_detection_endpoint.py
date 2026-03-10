# -*- coding: utf-8 -*-
"""
测试API检测端点
"""

import os
import sys
import asyncio
import aiohttp
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))


async def test_api_detection():
    """测试API检测端点"""
    print("=== 测试API检测端点 ===")

    base_url = "http://localhost:8000"
    test_image_path = "bus.jpg"

    if not os.path.exists(test_image_path):
        print(f"错误: 测试图片不存在: {test_image_path}")
        return False

    try:
        print("1. 检查服务器状态...")
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{base_url}/", timeout=5) as response:
                    if response.status == 200:
                        print("   服务器运行正常")
                    else:
                        print(f"   服务器返回状态码: {response.status}")
                        return False
            except aiohttp.ClientConnectorError:
                print("   服务器未运行，请先启动服务器")
                return False

        print("2. 测试检测API端点...")

        # 准备测试数据
        data = {
            "user_question": "检测这张图片中的目标",
            "image_path": os.path.abspath(test_image_path),
        }

        print(f"   请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

        # 发送请求到检测端点
        async with aiohttp.ClientSession() as session:
            try:
                print(f"   发送POST请求到: {base_url}/api/agent/mcp/process")
                async with session.post(
                    f"{base_url}/api/agent/mcp/process", json=data, timeout=30
                ) as response:
                    print(f"   响应状态码: {response.status}")

                    if response.status == 200:
                        result = await response.json()
                        print("   [OK] API调用成功")
                        print(
                            f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}"
                        )
                        return True
                    else:
                        print(f"   [ERROR] API调用失败，状态码: {response.status}")

                        # 尝试读取错误信息
                        try:
                            error_text = await response.text()
                            print(f"   错误响应: {error_text}")
                        except:
                            print("   无法读取错误响应")

                        return False

            except asyncio.TimeoutError:
                print("   [ERROR] 请求超时 (30秒)")
                return False
            except aiohttp.ClientConnectorError:
                print("   [ERROR] 无法连接到服务器")
                return False
            except Exception as e:
                print(f"   [ERROR] 请求失败: {type(e).__name__}: {str(e)}")
                return False

    except Exception as e:
        print(f"测试失败: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_simple_endpoint():
    """测试简单的端点"""
    print("\n=== 测试简单端点 ===")

    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/docs",
        "/redoc",
        "/api/health",
    ]

    try:
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                print(f"测试端点: {endpoint}")
                try:
                    async with session.get(
                        f"{base_url}{endpoint}", timeout=5
                    ) as response:
                        status = "[OK]" if response.status == 200 else "[WARN]"
                        print(f"  {status} 状态码: {response.status}")
                except aiohttp.ClientConnectorError:
                    print(f"  [ERROR] 无法连接到服务器")
                    return False
                except Exception as e:
                    print(f"  [ERROR] 错误: {type(e).__name__}: {e}")

        return True
    except Exception as e:
        print(f"测试失败: {type(e).__name__}: {str(e)}")
        return False


async def main():
    """主函数"""
    print("开始API端点测试...\n")

    # 检查服务器是否运行
    print("首先检查服务器状态...")

    try:
        import requests

        try:
            response = requests.get("http://localhost:8000/", timeout=5)
            print(f"服务器状态: [OK] 运行中 (状态码: {response.status})")
            server_running = True
        except requests.ConnectionError:
            print("服务器状态: [ERROR] 未运行")
            print("请先启动服务器: python main.py 或 uvicorn main:app --reload")
            server_running = False
    except ImportError:
        print("无法导入requests模块，跳过服务器检查")
        server_running = False

    # 运行测试
    tests = []

    if server_running:
        tests.append(("API检测端点", test_api_detection))
        tests.append(("简单端点", test_simple_endpoint))
    else:
        print("\n[WARN] 服务器未运行，跳过API测试")
        print("您可以：")
        print("1. 启动服务器后重新运行此测试")
        print("2. 检查服务器日志中的错误信息")

    results = []

    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        try:
            success = await test_func()
            results.append((test_name, success))
            status = "[OK] 通过" if success else "[ERROR] 失败"
            print(f"  结果: {status}")
        except Exception as e:
            print(f"  测试执行异常: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))

    # 汇总结果
    if results:
        print("\n=== 测试结果汇总 ===")
        passed = 0
        for test_name, success in results:
            status = "[OK] 通过" if success else "[ERROR] 失败"
            print(f"{test_name}: {status}")
            if success:
                passed += 1

        print(f"\n总计: {passed}/{len(results)} 个测试通过")
    else:
        print("\n[WARN] 没有运行任何测试")

    return len(results) > 0 and all(success for _, success in results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
