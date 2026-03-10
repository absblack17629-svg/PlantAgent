# -*- coding: utf-8 -*-
"""
修复编码问题 - 处理Windows控制台GBK编码问题
"""

import sys
import io


def fix_encoding():
    """
    修复Python在Windows上的编码问题
    """
    # 检查是否是Windows系统
    if sys.platform == "win32":
        try:
            # 尝试修改标准输出的编码为UTF-8
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
            print("✅ 已修复Windows控制台编码问题")
        except Exception as e:
            print(f"⚠️ 修复编码失败: {e}")
            # 使用ASCII安全模式
            print("⚠️ 使用ASCII安全模式")
    else:
        print("✅ 非Windows系统，无需修复编码")


if __name__ == "__main__":
    fix_encoding()
    print("测试中文字符：你好世界")
    print("测试emoji：✅ ❌ 🔍 ⚠️")
