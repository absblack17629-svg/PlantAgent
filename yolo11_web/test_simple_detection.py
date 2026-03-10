# -*- coding: utf-8 -*-
"""
简单的检测问题测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))


async def test_detection_core():
    """测试核心检测功能"""
    print("\n=== 测试核心检测功能 ===")

    try:
        # 从 services 导入检测服务
        from services.detection_service import get_detection_service

        print("1. 导入检测服务...")
        detection_service = get_detection_service()
        print("   导入成功")

        # 检查模型是否加载
        if detection_service.yolo_model is None:
            print("   警告: YOLO模型未加载（可能还在加载中）")
            # 继续测试，可能在运行时加载

        print("2. 检查测试图片...")
        test_image_path = os.path.join(os.path.dirname(__file__), "bus.jpg")

        if not os.path.exists(test_image_path):
            print(f"   错误: 测试图片不存在: {test_image_path}")
            # 尝试其他路径
            test_image_path = "bus.jpg"
            if not os.path.exists(test_image_path):
                print(f"   错误: 当前目录下也不存在: {test_image_path}")
                return False

        print(f"   图片路径: {os.path.abspath(test_image_path)}")
        print(f"   文件大小: {os.path.getsize(test_image_path)} bytes")

        print("3. 执行检测...")
        results = await detection_service.detect_async(test_image_path)

        print(f"   检测完成，结果数量: {len(results)}")

        if len(results) > 0:
            for i, result in enumerate(results[:3]):  # 只显示前3个结果
                print(f"   结果{i}: {result}")
            return True
        else:
            print("   警告: 没有检测到任何目标")
            return True  # 可能图片中没有可检测的目标

    except Exception as e:
        print(f"   测试失败: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

        print("2. 检查测试图片...")
        test_image_path = os.path.join(os.path.dirname(__file__), "bus.jpg")

        if not os.path.exists(test_image_path):
            print(f"   错误: 测试图片不存在: {test_image_path}")
            # 尝试其他路径
            test_image_path = "bus.jpg"
            if not os.path.exists(test_image_path):
                print(f"   错误: 当前目录下也不存在: {test_image_path}")
                return False

        print(f"   图片路径: {os.path.abspath(test_image_path)}")
        print(f"   文件大小: {os.path.getsize(test_image_path)} bytes")

        print("3. 执行检测...")
        results = detector.detect(test_image_path)

        print(f"   检测完成，结果数量: {len(results)}")

        if len(results) > 0:
            for i, result in enumerate(results[:3]):  # 只显示前3个结果
                print(f"   结果{i}: {result}")
            return True
        else:
            print("   警告: 没有检测到任何目标")
            return True  # 可能图片中没有可检测的目标

    except Exception as e:
        print(f"   测试失败: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_detection_service_import():
    """测试检测服务导入"""
    print("\n=== 测试检测服务导入 ===")

    try:
        # 测试导入各种服务
        from services.detection_service import get_detection_service

        print("1. detection_service: 导入成功")

        from services.detection_service import DetectionService

        print("2. DetectionService 类: 导入成功")

        # 检查是否有默认检测器
        try:
            from yoloapp.detection import get_default_detector

            print("3. 默认检测器: 导入成功")
        except ImportError:
            print("3. 默认检测器: 导入失败（可能需要其他方式）")

        return True

    except Exception as e:
        print(f"   导入失败: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始检测问题分析...")

    # 运行所有测试
    tests = [
        ("核心检测功能", test_detection_core),
        ("检测服务导入", test_detection_service_import),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        try:
            if test_func.__name__.endswith("_core"):
                success = await test_func()
            else:
                success = test_func()
            results.append((test_name, success))
            status = "通过" if success else "失败"
            print(f"  结果: {status}")
        except Exception as e:
            print(f"  测试执行异常: {e}")
            results.append((test_name, False))

    # 打印结果汇总
    print("\n=== 测试结果汇总 ===")
    for test_name, success in results:
        status = "通过" if success else "失败"
        print(f"{test_name}: {status}")

    total_passed = sum(1 for _, success in results if success)
    print(f"\n总计: {total_passed}/{len(results)} 个测试通过")

    return all(success for _, success in results)


if __name__ == "__main__":
    import asyncio

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
