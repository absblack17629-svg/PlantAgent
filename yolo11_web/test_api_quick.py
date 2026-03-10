# -*- coding: utf-8 -*-
"""
快速测试检测API
"""

import requests


def test_api():
    # 创建简单的测试文件
    with open("test.jpg", "wb") as f:
        f.write(b"fake image data")

    try:
        with open("test.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            response = requests.post(
                "http://localhost:8000/detection/upload", files=files
            )

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")

            if response.status_code == 200:
                print("API is working!")
                return True
            else:
                print("API failed")
                return False
    finally:
        import os

        if os.path.exists("test.jpg"):
            os.remove("test.jpg")


if __name__ == "__main__":
    print("Testing /detection/upload API...")
    test_api()
