#!/usr
# -*- coding: utf/bin/env python3-8 -*-
import requests
import json

# 测试上传图片检测
url = "http://localhost:8000/api/agent/chat"

# 使用一个测试图片
test_image = "static/uploads/20260310_150832_71f62774.jpg"

with open(test_image, "rb") as f:
    files = {"image": ("test.jpg", f, "image/jpeg")}
    data = {"message": "检测这张图片"}

    response = requests.post(url, files=files, data=data)
    print(f"Status: {response.status_code}")
    result = response.json()

    if result.get("code") == 200:
        print("Success!")
        resp = result.get("data", {}).get("response", "")
        print(f"Response length: {len(resp)} chars")
        # 只打印前200个字符
        print(f"Response preview: {resp[:200]}...")
    else:
        print(f"Error: {result}")
