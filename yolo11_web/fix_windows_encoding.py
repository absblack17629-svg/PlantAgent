# -*- coding: utf-8 -*-
"""
修复Windows编码问题 - 强制使用UTF-8
"""

import sys
import os
import io


def fix_windows_encoding():
    """修复Windows控制台编码问题"""
    if sys.platform == "win32":
        print("检测到Windows系统，修复编码问题...")

        # 方法1: 设置环境变量
        os.environ["PYTHONIOENCODING"] = "utf-8"

        # 方法2: 重定向标准输出
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
            print("标准输出已重定向到UTF-8")
        except Exception as e:
            print(f"重定向输出失败: {e}")

        # 方法3: 设置控制台代码页
        try:
            os.system("chcp 65001 > nul")  # UTF-8代码页
            print("控制台代码页已设置为UTF-8 (65001)")
        except Exception as e:
            print(f"设置代码页失败: {e}")

        # 方法4: 设置locale
        try:
            import locale

            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            print("locale已设置为UTF-8")
        except Exception as e:
            print(f"设置locale失败: {e}")

        print("Windows编码修复完成")
        return True
    else:
        print("非Windows系统，无需修复编码")
        return False


if __name__ == "__main__":
    fix_windows_encoding()

    # 测试修复效果
    test_strings = [
        "测试中文",
        "Test English",
        "[START][OK][HOT][PACKAGE][CELEBRATE]",  # emoji
        "[SEARCH][TOOL][TARGET][BOOK][MAP]",  # 更多emoji
    ]

    print("\n测试输出各种字符:")
    for s in test_strings:
        try:
            print(f"  {s}")
        except Exception as e:
            print(f"  输出失败: {type(e).__name__}: {e}")
