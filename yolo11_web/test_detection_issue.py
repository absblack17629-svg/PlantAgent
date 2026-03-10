# -*- coding: utf-8 -*-
"""
测试检测问题：
1. 测试直接调用检测服务
2. 测试通过API调用检测
3. 分析路径和权限问题
"""

import os
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))


async def test_direct_detection():
    """直接调用检测服务测试"""
    print("\n" + "=" * 60)
    print("1. 直接调用检测服务测试")
    print("=" * 60)

    try:
        from services.detection_service import get_detection_service

        # 获取检测服务
        detection_service = get_detection_service()

        # 检查模型是否加载
        if detection_service.yolo_model is None:
            print("[ERROR] 检测服务: YOLO模型未加载")
            return False
        else:
            print("[OK] 检测服务: YOLO模型已加载")

        # 测试图片路径
        test_image_path = "static/uploads/20260310_150832_71f62774.jpg"

        # 检查图片是否存在
        if not os.path.exists(test_image_path):
            print(f"[ERROR] 测试图片不存在: {test_image_path}")
            # 尝试使用绝对路径
            test_image_path = os.path.join(os.getcwd(), test_image_path)
            print(f"   尝试绝对路径: {test_image_path}")
            if not os.path.exists(test_image_path):
                print(f"[ERROR] 绝对路径图片也不存在")
                return False

        print(f"[OK] 测试图片存在: {test_image_path}")
        print(f"   文件大小: {os.path.getsize(test_image_path)} bytes")

        # 执行检测
        print("[DETECT] 执行检测...")
        results = await detection_service.detect_objects(test_image_path)

        print(f"[OK] 检测完成，结果数量: {len(results)}")
        if results:
            for i, result in enumerate(results[:3], 1):
                print(f"   结果{i}: {result}")
        else:
            print("   没有检测到任何目标")

        return True

    except Exception as e:
        print(f"[ERROR] 直接检测测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_api_detection():
    """通过API调用检测测试"""
    print("\n" + "=" * 60)
    print("2. 通过API调用检测测试")
    print("=" * 60)

    try:
        # 模拟API调用
        from routers.mcp_agent import chat_with_agent

        # 创建模拟请求
        test_message = "检测这张图片中的水稻病害"
        test_image_path = "static/uploads/20260310_150832_71f62774.jpg"

        print(f"[NOTE] 测试消息: {test_message}")
        print(f"[CAMERA] 测试图片: {test_image_path}")

        # 注意：这里需要模拟FastAPI的请求对象
        # 由于依赖关系复杂，我们只检查路径和权限

        # 检查图片文件权限
        if os.path.exists(test_image_path):
            import stat

            mode = os.stat(test_image_path).st_mode
            print(f"[OK] 图片文件权限: {oct(mode)}")
            print(f"   可读: {bool(mode & stat.S_IRUSR)}")
            print(f"   可写: {bool(mode & stat.S_IWUSR)}")

        # 检查上传目录权限
        upload_dir = "static/uploads"
        if os.path.exists(upload_dir):
            print(f"[OK] 上传目录存在: {upload_dir}")
            # 检查目录权限
            try:
                test_file = os.path.join(upload_dir, "test_permission.txt")
                with open(test_file, "w") as f:
                    f.write("test")
                os.remove(test_file)
                print("[OK] 上传目录有写入权限")
            except Exception as e:
                print(f"[ERROR] 上传目录写入权限失败: {e}")

        return True

    except Exception as e:
        print(f"[ERROR] API检测测试失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


async def test_path_issues():
    """测试路径相关问题"""
    print("\n" + "=" * 60)
    print("3. 路径相关问题测试")
    print("=" * 60)

    try:
        # 测试各种路径格式
        test_paths = [
            "static/uploads/20260310_150832_71f62774.jpg",
            "./static/uploads/20260310_150832_71f62774.jpg",
            os.path.join(os.getcwd(), "static/uploads/20260310_150832_71f62774.jpg"),
            os.path.normpath("static/uploads/20260310_150832_71f62774.jpg"),
        ]

        for path in test_paths:
            exists = os.path.exists(path)
            print(f"路径: {path}")
            print(f"  存在: {'[OK]' if exists else '[ERROR]'}")
            if exists:
                print(f"  大小: {os.path.getsize(path)} bytes")
                print(f"  绝对路径: {os.path.abspath(path)}")

        # 检查当前工作目录
        print(f"\n[FOLDER] 当前工作目录: {os.getcwd()}")

        # 检查Python路径
        print(f"[PYTHON] Python路径:")
        for path in sys.path[:5]:
            print(f"  {path}")

        return True

    except Exception as e:
        print(f"[ERROR] 路径测试失败: {str(e)}")
        return False


async def test_detection_service_import():
    """测试检测服务导入问题"""
    print("\n" + "=" * 60)
    print("4. 检测服务导入测试")
    print("=" * 60)

    try:
        # 尝试导入所有相关模块
        modules_to_test = [
            "services.detection_service",
            "yoloapp.tool.detection_tool",
            "yoloapp.tool.langchain_tools",
            "yoloapp.flow.nine_node_with_tools",
        ]

        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"[OK] {module_name}: 导入成功")
            except Exception as e:
                print(f"[ERROR] {module_name}: 导入失败 - {e}")

        return True

    except Exception as e:
        print(f"[ERROR] 导入测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("开始检测问题分析...")

    # 运行所有测试
    tests = [
        ("直接检测服务", test_direct_detection),
        ("API检测路径", test_api_detection),
        ("路径问题", test_path_issues),
        ("导入测试", test_detection_service_import),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n[TOOL] 运行测试: {test_name}")
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"[ERROR] 测试执行异常: {e}")
            results.append((test_name, False))

    # 打印结果汇总
    print("\n" + "=" * 60)
    print("[CHART] 测试结果汇总")
    print("=" * 60)

    for test_name, success in results:
        status = "[OK] 通过" if success else "[ERROR] 失败"
        print(f"{test_name:20} {status}")

    # 分析可能的问题
    print("\n" + "=" * 60)
    print("[DETECT] 可能的问题分析")
    print("=" * 60)

    # 检查常见的Windows路径问题
    if os.name == "nt":  # Windows
        print("[NET] 系统: Windows")
        print("[TIP] 可能的问题:")
        print("  1. 路径分隔符问题（Windows使用反斜杠）")
        print("  2. 文件权限问题（特别是从其他位置复制文件）")
        print("  3. 编码问题（非ASCII字符）")
    else:
        print("[PENGUIN] 系统: Linux/Mac")
        print("[TIP] 可能的问题:")
        print("  1. 文件权限问题（chmod）")
        print("  2. 路径区分大小写")

    # 检查具体文件
    image_path = "static/uploads/20260310_150832_71f62774.jpg"
    if os.path.exists(image_path):
        print(f"\n[CAMERA] 测试图片详细信息:")
        print(f"  路径: {os.path.abspath(image_path)}")
        print(f"  大小: {os.path.getsize(image_path)} bytes")
        print(f"  修改时间: {os.path.getmtime(image_path)}")

        # 检查文件是否为有效图片
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                print(f"  图片格式: {img.format}")
                print(f"  图片尺寸: {img.size}")
                print(f"  图片模式: {img.mode}")
                print("[OK] 图片文件有效")
        except Exception as e:
            print(f"[ERROR] 图片文件可能损坏: {e}")
    else:
        print(f"\n[ERROR] 测试图片不存在: {image_path}")
        # 列出上传目录内容
        upload_dir = "static/uploads"
        if os.path.exists(upload_dir):
            print(f"[FOLDER] 上传目录内容:")
            for item in os.listdir(upload_dir)[:10]:
                print(f"  {item}")
        else:
            print(f"[FOLDER] 上传目录不存在: {upload_dir}")

    print("\n[TARGET] 建议的解决方案:")
    print("  1. 确保图片路径正确且可访问")
    print("  2. 检查文件权限（Windows: 右键属性->安全）")
    print("  3. 尝试使用绝对路径而不是相对路径")
    print("  4. 检查YOLO模型是否已正确加载")
    print("  5. 查看服务器日志获取详细错误信息")


if __name__ == "__main__":
    asyncio.run(main())
