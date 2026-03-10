# -*- coding: utf-8 -*-
"""
测试检测API是否正常工作
"""

import requests
import json
import os


def test_detection_api():
    """测试检测API"""

    # API地址
    api_url = "http://localhost:8000/detection/upload"

    # 测试图片路径 - 使用一个简单的测试图片
    # 首先检查是否有测试图片
    test_image_path = "test_image.jpg"

    # 如果没有测试图片，创建一个虚拟的
    if not os.path.exists(test_image_path):
        print("没有找到测试图片，创建一个虚拟图片...")
        # 创建一个简单的测试图片（1x1像素的黑色图片）
        from PIL import Image

        img = Image.new("RGB", (1, 1), color="black")
        img.save(test_image_path)
        print(f"已创建测试图片: {test_image_path}")

    try:
        # 准备上传文件
        with open(test_image_path, "rb") as f:
            files = {"file": (os.path.basename(test_image_path), f, "image/jpeg")}

            print(f"上传文件到 {api_url}...")
            response = requests.post(api_url, files=files)

            print(f"响应状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print(f"API调用成功!")
                print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return True
            else:
                print(f"API调用失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试检测API...")
    success = test_detection_api()

    if success:
        print("检测API测试通过!")
    else:
        print("检测API测试失败，请检查后端服务是否正常运行")
