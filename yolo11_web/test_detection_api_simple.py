# -*- coding: utf-8 -*-
"""
简单测试检测API
"""

import requests
import json
import os


def test_detection_api():
    """测试检测API"""
    print("测试检测API...")

    base_url = "http://localhost:8000"
    test_image_path = "bus.jpg"

    if not os.path.exists(test_image_path):
        print(f"错误: 测试图片不存在: {test_image_path}")
        return False

    # 测试多个API端点
    endpoints = [
        {
            "name": "MCP Agent检测",
            "url": f"{base_url}/api/agent/mcp/process",
            "data": {
                "user_question": "检测这张图片中的目标",
                "image_path": os.path.abspath(test_image_path),
            },
        },
        {
            "name": "LangGraph检测",
            "url": f"{base_url}/api/langgraph/process",
            "data": {
                "user_question": "检测这张图片中的目标",
                "image_path": os.path.abspath(test_image_path),
            },
        },
        {
            "name": "直接检测API",
            "url": f"{base_url}/api/detect",
            "files": {"file": open(test_image_path, "rb")},
        },
    ]

    results = []

    for endpoint in endpoints:
        print(f"\n测试端点: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")

        try:
            if "files" in endpoint:
                # 文件上传测试
                print("  类型: 文件上传")
                response = requests.post(endpoint["url"], files=endpoint["files"])
            else:
                # JSON数据测试
                print("  类型: JSON数据")
                print(
                    f"  数据: {json.dumps(endpoint['data'], ensure_ascii=False, indent=2)}"
                )
                response = requests.post(
                    endpoint["url"], json=endpoint["data"], timeout=30
                )

            print(f"  状态码: {response.status_code}")

            if response.status_code == 200:
                print("  [OK] 成功")
                try:
                    result = response.json()
                    print(
                        f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}..."
                    )
                except:
                    print(f"  响应文本: {response.text[:500]}...")
                results.append((endpoint["name"], True))
            else:
                print("  [ERROR] 失败")
                print(f"  错误响应: {response.text[:500]}")
                results.append((endpoint["name"], False))

        except requests.exceptions.Timeout:
            print("  [ERROR] 请求超时 (30秒)")
            results.append((endpoint["name"], False))
        except requests.exceptions.ConnectionError:
            print("  [ERROR] 无法连接到服务器")
            results.append((endpoint["name"], False))
        except Exception as e:
            print(f"  [ERROR] 请求失败: {type(e).__name__}: {str(e)}")
            results.append((endpoint["name"], False))

    # 关闭所有打开的文件
    for endpoint in endpoints:
        if "files" in endpoint:
            for file in endpoint["files"].values():
                if hasattr(file, "close"):
                    file.close()

    # 汇总结果
    print("\n=== 测试结果汇总 ===")
    passed = 0
    for test_name, success in results:
        status = "[OK] 通过" if success else "[ERROR] 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 个测试通过")

    return passed > 0


def test_health_endpoints():
    """测试健康检查端点"""
    print("\n=== 测试健康检查端点 ===")

    base_url = "http://localhost:8000"
    endpoints = [
        ("根路径", "/"),
        ("API文档", "/docs"),
        ("备用文档", "/redoc"),
        ("健康检查", "/api/health"),
        ("监控状态", "/api/monitoring/status"),
    ]

    results = []

    for name, endpoint in endpoints:
        print(f"测试: {name} ({endpoint})")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "[OK]" if response.status_code == 200 else "[WARN]"
            print(f"  状态: {status} {response.status_code}")
            results.append((name, response.status_code == 200))
        except Exception as e:
            print(f"  [ERROR] 失败: {type(e).__name__}")
            results.append((name, False))

    return all(success for _, success in results)


if __name__ == "__main__":
    print("开始API测试...")

    # 检查服务器
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"服务器状态: [OK] 运行中 (状态码: {response.status_code})")
    except:
        print("服务器状态: [ERROR] 未运行")
        print("请先启动服务器: python main.py")
        exit(1)

    # 运行测试
    health_ok = test_health_endpoints()
    api_ok = test_detection_api()

    if not api_ok:
        print("\n[WARN] 检测API存在问题，建议:")
        print("1. 检查服务器日志中的错误信息")
        print("2. 确认检测服务已正确加载")
        print("3. 检查API路由是否正确配置")

    print("\n测试完成")
