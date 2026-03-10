# -*- coding: utf-8 -*-
"""
纯ASCII检测测试 - 不使用任何Unicode字符
"""

import asyncio
import sys
import os

sys.path.append(".")


async def test_detection():
    """测试检测服务"""
    print("Testing detection service...")

    try:
        from services.detection_service import get_detection_service

        service = get_detection_service()
        print("Service loaded")

        # 使用测试图片
        test_image = "bus.jpg"
        if os.path.exists(test_image):
            print(f"Testing with image: {test_image}")
            results = await service.detect_objects(test_image)
            print(f"Detection results: {results}")
            return True
        else:
            print(f"Test image not found: {test_image}")
            return False

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_detection())
    sys.exit(0 if success else 1)
