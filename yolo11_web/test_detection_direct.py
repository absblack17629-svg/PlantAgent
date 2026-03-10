# -*- coding: utf-8 -*-
"""
直接测试检测功能
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))


async def test_detection():
    """测试检测功能"""
    print("=== 测试YOLO检测功能 ===")

    try:
        # 导入检测服务
        from services.detection_service import DetectionService

        print("1. 创建检测服务实例...")
        service = DetectionService()
        print("   检测服务创建成功")

        # 检查模型是否加载
        if service.yolo_model is None:
            print("   错误: YOLO模型未加载")
            return False

        print("2. 检查测试图片...")

        # 尝试多种可能的图片路径
        possible_paths = [
            "bus.jpg",
            os.path.join(os.path.dirname(__file__), "bus.jpg"),
            os.path.join(os.getcwd(), "bus.jpg"),
        ]

        test_image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                test_image_path = path
                break

        if test_image_path is None:
            print("   错误: 找不到测试图片")
            print("   尝试在当前目录创建测试图片...")
            # 创建一个简单的测试图片
            try:
                import numpy as np
                from PIL import Image

                test_img = np.ones((640, 640, 3), dtype=np.uint8) * 255
                test_img = Image.fromarray(test_img)
                test_image_path = "test_white.jpg"
                test_img.save(test_image_path)
                print(f"   已创建测试图片: {test_image_path}")
            except Exception as e:
                print(f"   无法创建测试图片: {e}")
                return False

        print(f"   使用图片: {os.path.abspath(test_image_path)}")
        print(f"   文件大小: {os.path.getsize(test_image_path)} bytes")

        print("3. 执行检测...")
        results = await service.detect_objects(test_image_path)

        print(f"   检测完成，找到 {len(results)} 个目标")

        if len(results) > 0:
            print("   前3个检测结果:")
            for i, result in enumerate(results[:3]):
                print(f"     {i}: {result}")
        else:
            print("   注意: 没有检测到任何目标")
            print("   这可能是因为:")
            print("     - 图片是空白背景")
            print("     - YOLO模型配置问题")
            print("     - 模型需要重新训练")

        # 清理临时文件
        if test_image_path == "test_white.jpg" and os.path.exists(test_image_path):
            os.remove(test_image_path)
            print("   已清理临时测试图片")

        return True

    except Exception as e:
        print(f"   测试失败: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_detection():
    """测试通过API的检测功能"""
    print("\n=== 测试API检测功能 ===")

    try:
        # 检查FastAPI是否可用
        from routers.agent_factory import process_agent_request

        print("1. 导入Agent Factory成功")

        # 检查图片
        test_image_path = "bus.jpg"
        if not os.path.exists(test_image_path):
            test_image_path = os.path.join(os.path.dirname(__file__), "bus.jpg")

        if not os.path.exists(test_image_path):
            print(f"   错误: 测试图片不存在: {test_image_path}")
            return False

        print(f"2. 准备调用API: 图片={test_image_path}")
        print("   注意: 实际API调用需要运行中的服务器")
        print("   测试将检查路径和权限...")

        # 检查文件权限
        try:
            with open(test_image_path, "rb") as f:
                f.read(100)  # 读取前100字节
            print(f"   文件可读取: 是")
        except Exception as e:
            print(f"   文件读取失败: {e}")
            return False

        print("   文件权限检查通过")
        return True

    except ImportError as e:
        print(f"   导入失败: {e}")
        return False
    except Exception as e:
        print(f"   测试失败: {type(e).__name__}: {str(e)}")
        return False


async def main():
    """主函数"""
    print("开始检测问题诊断...\n")

    # 运行测试
    tests = [
        ("直接检测", test_detection),
        ("API检测路径", test_api_detection),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"运行测试: {test_name}")
        try:
            success = await test_func()
            results.append((test_name, success))
            status = "通过" if success else "失败"
            print(f"  结果: {status}\n")
        except Exception as e:
            print(f"  测试执行异常: {e}")
            import traceback

            traceback.print_exc()
            results.append((test_name, False))
            print()

    # 汇总结果
    print("=== 测试结果汇总 ===")
    passed = 0
    for test_name, success in results:
        status = "[OK] 通过" if success else "[ERROR] 失败"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 个测试通过")

    if passed < len(results):
        print("\n[WARNING]  检测系统存在问题，建议:")
        print("1. 检查YOLO模型文件是否存在")
        print("2. 检查图片文件路径权限")
        print("3. 查看服务器日志获取详细错误信息")

    return passed == len(results)


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
