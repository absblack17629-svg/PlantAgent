#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试检测功能"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.detection_service import get_detection_service


async def test_detection():
    print("测试检测...")

    # 获取检测服务
    service = get_detection_service()

    # 使用一个实际的测试图片
    test_path = "static/uploads/20260310_150832_71f62774.jpg"

    if os.path.exists(test_path):
        print(f"执行检测: {test_path}")
        results = await service.detect_objects(test_path)
        print(f"检测结果: {results}")
    else:
        print("图片不存在")


if __name__ == "__main__":
    asyncio.run(test_detection())
