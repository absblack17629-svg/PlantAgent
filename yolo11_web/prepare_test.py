# -*- coding: utf-8 -*-
"""
前端测试准备脚本 - 自动复制测试图片并生成测试指南
"""

import shutil
import random
import os
from pathlib import Path

# 测试图片源目录
SOURCE_DIR = Path("C:/yolov8/ultralytics-8.0.224/yolov8_dataset/train/images")
# 测试图片目标目录（前端可访问）
TEST_DIR = Path("C:/Users/1/Desktop/file/Fastapi_backend/yolo11_web/static/test_images")

def select_test_images():
    """随机选择5张测试图片"""
    if not SOURCE_DIR.exists():
        print(f"❌ 源目录不存在: {SOURCE_DIR}")
        return []
    
    all_images = list(SOURCE_DIR.glob("*.jpg")) + list(SOURCE_DIR.glob("*.png"))
    
    if len(all_images) == 0:
        print(f"❌ 未找到图片文件")
        return []
    
    # 随机选择5张
    selected = random.sample(all_images, min(5, len(all_images)))
    return selected

def copy_test_images():
    """复制测试图片到测试目录"""
    # 创建测试目录
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # 选择图片
    images = select_test_images()
    
    if not images:
        return False
    
    print("\n" + "="*60)
    print("已选择以下测试图片：")
    print("="*60)
    
    copied = []
    for i, img_path in enumerate(images, 1):
        dest_path = TEST_DIR / img_path.name
        try:
            shutil.copy2(img_path, dest_path)
            copied.append(dest_path)
            print(f"{i}. {img_path.name}")
            print(f"   复制到: {dest_path}")
        except Exception as e:
            print(f"{i}. {img_path.name} - 复制失败: {e}")
    
    return copied

def print_test_guide():
    """打印测试指南"""
    guide = """
====================================================================
                     🌾 水稻病害智能助手 - 测试指南
====================================================================

一、启动服务
============

1. 启动后端服务（窗口1）：
   cd C:/Users/1/Desktop/file/Fastapi_backend/yolo11_web
   python main.py

2. 启动前端服务（窗口2）：
   cd C:/Users/1/Desktop/file/Fastapi_backend/yolo11_web/frontend
   npm run dev

二、访问系统
============

浏览器访问：http://localhost:3000

三、测试用例
============

【测试1】问候语
-------------
输入：你好
预期：返回友好的问候语

【测试2】知识查询
-----------------
输入：什么是稻瘟病？
预期：返回稻瘟病的详细说明和防治方法

【测试3】图片检测（重要！）
--------------------------
步骤：
1. 点击智能助手界面中的图片上传按钮
2. 选择以下任一测试图片：
"""
    
    # 列出测试图片
    if TEST_DIR.exists():
        test_images = list(TEST_DIR.glob("*.jpg")) + list(TEST_DIR.glob("*.png"))
        for i, img in enumerate(test_images[:5], 1):
            guide += f"   {i}. {img.name}\n"
    
    guide += """
3. 输入：帮我检测这张图片的病害

预期结果：
✅ 显示"🔬 检测到 X 个对象..."
❌ 不应该显示"🔬 mock"或错误信息

【测试4】虫害查询
-----------------
输入：稻飞虱怎么防治？
预期：返回稻飞虱的危害特点和防治措施

四、预期调试日志
================

在测试过程中，后端控制台会输出详细的调试日志：

[9-Node] Input: 你好... image_path=None
[9-Node] skill_client available: True
[9-Node] Running agent: intent
[9-Node] Running agent: context
...
[9-Node] Final response: 你好！我是水稻病害智能助手🌾 ...

五、常见问题排查
================

问题1：检测返回"mock"
解决：检查后端日志中 [9-Node] skill_client available 是否为 True

问题2：知识查询返回"抱歉"
解决：知识库已扩充，如仍有问题请检查 RAG 服务是否正常初始化

问题3：图片上传失败
解决：检查图片格式是否为 jpg 或 png

====================================================================
                        祝您测试顺利！
====================================================================
"""
    print(guide)

def main():
    print("\n" + "="*60)
    print("   水稻病害智能助手 - 测试准备工具")
    print("="*60)
    
    # 复制测试图片
    copied = copy_test_images()
    
    if copied:
        print(f"\n✅ 成功复制 {len(copied)} 张测试图片")
        # 打印测试指南
        print_test_guide()
    else:
        print("\n❌ 测试图片准备失败")
        print("\n可能的解决方案：")
        print("1. 检查源目录是否存在:", SOURCE_DIR)
        print("2. 检查是否有图片文件 (.jpg, .png)")
        print("3. 手动复制图片到:", TEST_DIR)

if __name__ == "__main__":
    main()
