# -*- coding: utf-8 -*-
"""
UTF-8启动脚本 - 修复Windows控制台编码问题
在Windows上运行时自动修复编码，保留emoji支持
"""

import os
import sys
import subprocess
import io


def fix_windows_encoding():
    """修复Windows控制台编码"""
    if sys.platform == "win32":
        # 检查当前编码
        current_encoding = sys.stdout.encoding
        print(f"当前控制台编码: {current_encoding}")

        # 如果是GBK，修复为UTF-8
        if current_encoding == "gbk" or current_encoding == "cp936":
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace"
                )
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace"
                )
                print("✅ 控制台编码已修复为UTF-8")
                print("🎉 现在可以正常显示emoji: 🔍 ✅ ❌ ⚠️ 📊")
            except Exception as e:
                print(f"⚠️ 修复编码失败: {e}")
        else:
            print(f"✅ 当前编码已经是 {current_encoding}，无需修复")
    else:
        print("✅ 非Windows系统，无需修复编码")


def main():
    """主函数"""
    fix_windows_encoding()

    # 运行实际的测试脚本
    print("\n" + "=" * 50)
    print("运行病害检测API测试...")
    print("=" * 50 + "\n")

    try:
        # 导入并运行测试
        import test_real_api

        test_real_api.test_real_api()
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
