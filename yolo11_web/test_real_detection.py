#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实的检测测试 - 模拟前端上传
"""

import requests
import json
import os


def test_real_upload():
    """模拟前端上传文件"""
    print("测试真实的上传检测...")

    # 后端API地址
    base_url = "http://localhost:8000"

    # 检查测试图片
    test_image = "bus.jpg"
    if not os.path.exists(test_image):
        print(f"测试图片不存在: {test_image}")
        # 创建一个简单的测试图片
        try:
            from PIL import Image
            import numpy as np

            img = Image.new("RGB", (640, 640), color=(255, 255, 255))
            img.save(test_image)
            print(f"已创建测试图片: {test_image}")
        except:
            print("无法创建测试图片")
            return False

    print(f"使用图片: {os.path.abspath(test_image)}")

    # 准备上传
    files = {"file": (test_image, open(test_image, "rb"), "image/jpeg")}

    try:
        print(f"POST到: {base_url}/api/detection/upload")
        response = requests.post(
            f"{base_url}/api/detection/upload", files=files, timeout=30
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("检测成功!")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"失败: {response.status_code}")
            print(f"响应: {response.text}")

            # 检查是否是Unicode编码问题
            if "UnicodeEncodeError" in response.text:
                print("\n发现Unicode编码问题")
                print("建议修复后端代码中的print语句")

            return False

    except Exception as e:
        print(f"请求异常: {type(e).__name__}: {str(e)}")
        return False
    finally:
        # 确保文件被关闭
        if "file" in locals():
            try:
                files["file"][1].close()
            except:
                pass


def check_endpoint_direct():
    """直接检查API端点"""
    print("\n直接检查API端点...")

    import urllib.request
    import urllib.error

    base_url = "http://localhost:8000"
    endpoint = "/api/detection/upload"

    try:
        # 测试GET方法
        request = urllib.request.Request(f"{base_url}{endpoint}")
        response = urllib.request.urlopen(request, timeout=5)
        print(f"GET {endpoint} - 状态: {response.status}")
        print("警告: GET方法应该返回405")
        return False
    except urllib.error.HTTPError as e:
        if e.code == 405:
            print(f"GET {endpoint} - 正确返回405 (Method Not Allowed)")
            return True
        else:
            print(f"GET {endpoint} - 错误状态: {e.code}")
            return False
    except Exception as e:
        print(f"GET {endpoint} - 异常: {type(e).__name__}")
        return False


if __name__ == "__main__":
    print("开始真实的检测测试...")

    # 首先检查API端点是否正确
    if not check_endpoint_direct():
        print("API端点配置可能有问题")

    # 测试真实的上传
    if test_real_upload():
        print("\n测试通过!")
        print("前端可能的问题:")
        print("1. JavaScript错误 - 检查浏览器Console")
        print("2. CORS问题 - 检查Network标签")
        print("3. 文件上传格式错误")
    else:
        print("\n测试失败!")
        print("需要检查:")
        print("1. 后端服务器是否运行")
        print("2. 检测服务是否加载")
        print("3. API路由是否正确")
