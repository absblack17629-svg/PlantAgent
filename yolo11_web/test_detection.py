#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试检测功能"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.detection_service import get_detection_service


async def test_detection():
    print("测试检测服务...")

    # 获取检测服务
    service = get_detection_service()

    # 检查模型
    if service.yolo_model is None:
        print("错误: 模型未加载")
        return

    print(f"模型已加载: {service.yolo_model}")

    # 测试检测 - 使用一个测试图片路径
    test_path = "test.jpg"
    if not os.path.exists(test_path):
        print(f"测试图片不存在: {test_path}")
        # 尝试找其他图片
        uploads = "static/uploads"
        if os.path.exists(uploads):
            files = os.listdir(uploads)
            if files:
                test_path = os.path.join(uploads, files[0])
                print(f"使用上传的图片: {test_path}")

    if os.path.exists(test_path):
        print(f"执行检测: {test_path}")
        results = await service.detect_objects(test_path)
        print(f"检测结果: {results}")
    else:
        print("没有可用的测试图片")


if __name__ == "__main__":
    asyncio.run(test_detection())
