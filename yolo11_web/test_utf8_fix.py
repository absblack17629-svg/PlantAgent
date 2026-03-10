#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试UTF-8编码修复

验证全局UTF-8编码设置是否解决了GBK编码错误。
"""

import sys
import os


def test_utf8_encoding():
    """测试UTF-8编码"""
    print("开始UTF-8编码测试...")

    # 测试字符串包含各种问题字符
    test_cases = [
        # 包含问题emoji的字符串
        ("🔍 搜索测试", "包含搜索emoji"),
        ("✅ 成功测试", "包含成功emoji"),
        ("❌ 错误测试", "包含错误emoji"),
        ("⚠️ 警告测试", "包含警告emoji"),
        ("📊 图表测试", "包含图表emoji"),
        ("🌾 水稻测试", "包含水稻emoji"),
        # 包含中文字符
        ("中文字符测试", "纯中文字符"),
        ("中文🔍混合测试", "中英混合加emoji"),
        # 特殊字符
        ("特殊字符: àéîöü", "特殊拉丁字符"),
        ("特殊字符: 日本語", "日文字符"),
        ("特殊字符: 한국어", "韩文字符"),
    ]

    all_passed = True

    for test_text, description in test_cases:
        try:
            # 尝试编码为UTF-8
            encoded = test_text.encode("utf-8")
            decoded = encoded.decode("utf-8")

            # 尝试打印（这通常会触发GBK错误）
            print(f"✅ {description}: {test_text}")

        except UnicodeEncodeError as e:
            print(f"❌ {description}: 编码失败 - {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ {description}: 其他错误 - {e}")
            all_passed = False

    return all_passed


def test_current_encoding():
    """测试当前系统编码"""
    print("\n当前系统编码信息:")
    print(f"平台: {sys.platform}")
    print(f"Python版本: {sys.version}")
    print(f"默认编码: {sys.getdefaultencoding()}")
    print(f"文件系统编码: {sys.getfilesystemencoding()}")
    print(f"环境变量 PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未设置')}")
    print(f"环境变量 PYTHONUTF8: {os.environ.get('PYTHONUTF8', '未设置')}")

    # 测试stdout编码
    try:
        if hasattr(sys.stdout, "encoding"):
            print(f"标准输出编码: {sys.stdout.encoding}")
        else:
            print("标准输出编码: 无法获取")
    except:
        print("标准输出编码: 获取失败")


def main():
    """主测试函数"""
    print("=" * 60)
    print("UTF-8编码修复测试")
    print("=" * 60)

    # 先显示当前编码状态
    test_current_encoding()

    print("\n" + "=" * 60)
    print("开始UTF-8编码测试...")
    print("=" * 60)

    # 应用强制UTF-8设置
    from yoloapp.utils.encoding import force_global_utf8

    force_global_utf8()

    # 再次显示编码状态
    test_current_encoding()

    print("\n" + "=" * 60)
    print("测试具体字符串编码...")
    print("=" * 60)

    # 运行测试
    if test_utf8_encoding():
        print("\n✅ 所有UTF-8编码测试通过！")
        print("✅ 编码问题应该已解决")
    else:
        print("\n❌ 某些测试失败")
        print("❌ 可能需要进一步处理编码问题")

    print("\n使用说明:")
    print("1. 在main.py中调用 force_global_utf8()")
    print("2. 或者导入: from yoloapp.utils.encoding import force_global_utf8")
    print("3. 运行此脚本验证修复效果")


if __name__ == "__main__":
    main()
