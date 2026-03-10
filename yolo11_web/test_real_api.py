# -*- coding: utf-8 -*-
"""
测试真正的病害检测API
"""

import requests
from PIL import Image
import os


def test_real_api():
    # 创建一个测试图片
    img = Image.new("RGB", (100, 100), color="green")
    img.save("test_image.jpg", "JPEG")

    try:
        with open("test_image.jpg", "rb") as f:
            files = {"file": ("test_image.jpg", f, "image/jpeg")}

            print("测试 /api/detection/upload...")
            response = requests.post(
                "http://localhost:8000/api/detection/upload", files=files
            )

            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text[:500]}...")

            if response.status_code == 200:
                print("[SUCCESS] API工作正常!")
                result = response.json()
                print(f"检测结果: {result.get('disease_type', '未知')}")
                return True
            else:
                print("[FAILURE] API调用失败")
                return False
    finally:
        if os.path.exists("test_image.jpg"):
            os.remove("test_image.jpg")


if __name__ == "__main__":
    test_real_api()
