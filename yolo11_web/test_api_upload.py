# -*- coding: utf-8 -*-
"""
纯ASCII API上传测试
"""

import requests
import json
import os
import sys


def test_upload():
    """测试文件上传API"""
    print("Testing file upload API...")

    url = "http://localhost:8000/api/detection/upload"

    # 使用bus.jpg测试
    test_file = "bus.jpg"
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return False

    try:
        # 准备文件上传
        files = {"file": ("bus.jpg", open(test_file, "rb"), "image/jpeg")}

        # 发送请求
        print(f"POST to: {url}")
        response = requests.post(url, files=files, timeout=30)

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', False)}")
            print(f"Response keys: {list(result.keys())}")
            return True
        else:
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"Request error: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    # 首先检查服务器是否运行
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Server status: RUNNING (status: {response.status_code})")

        # 运行测试
        success = test_upload()
        sys.exit(0 if success else 1)

    except requests.ConnectionError:
        print("Server status: NOT RUNNING")
        print("Please start server: python main.py")
        sys.exit(1)
