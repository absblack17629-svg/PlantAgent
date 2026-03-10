# -*- coding: utf-8 -*-
"""
纯ASCII增强检测测试
"""

import asyncio
import sys
import os

sys.path.append(".")


async def test_enhanced_detection():
    """测试增强检测服务"""
    print("Testing enhanced detection service...")

    try:
        from services.enhanced_detection_service import get_enhanced_detection_service

        service = get_enhanced_detection_service()
        print("Enhanced service loaded")

        # 使用测试图片
        test_image = "bus.jpg"
        if os.path.exists(test_image):
            print(f"Testing with image: {test_image}")
            result = await service.detect(test_image)
            print(f"Enhanced detection result keys: {list(result.keys())}")
            print(f"Success: {result.get('success', False)}")
            print(f"Disease found: {result.get('disease_found', False)}")
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
    success = asyncio.run(test_enhanced_detection())
    sys.exit(0 if success else 1)
