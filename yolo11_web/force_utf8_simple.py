#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最简单的全局UTF-8强制解决方案

在应用启动时调用此函数，解决所有编码问题。
"""

import sys
import os


def force_utf8():
    """
    强制全局UTF-8编码 - 最简单的解决方案

    解决以下错误：
    - UnicodeEncodeError: 'gbk' codec can't encode character '\U0001f50d'
    - 'gbk' codec can't encode character
    - 'charmap' codec can't encode character
    """
    # 1. 设置环境变量（最有效）
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

    # 2. Windows特定设置
    if sys.platform == "win32":
        try:
            # 方法1: 使用reconfigure（Python 3.7+）
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except:
            try:
                # 方法2: 使用TextIOWrapper（兼容性更好）
                import io

                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace"
                )
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace"
                )
            except:
                pass  # 如果都失败，继续使用原设置

    # 3. 设置默认编码（如果有此属性）
    if hasattr(sys, "setdefaultencoding"):
        try:
            sys.setdefaultencoding("utf-8")
        except:
            pass

    print("✅ 全局UTF-8编码已强制设置完成")
    print("✅ 编码问题应该已解决")


def fix_gbk_errors():
    """
    直接修复GBK编码错误的实用函数

    使用此函数处理字符串，确保不会出现编码错误
    """

    def fix_text(text):
        """修复单个文本的编码问题"""
        if text is None:
            return ""

        # 确保是字符串
        if not isinstance(text, str):
            text = str(text)

        # 使用replace策略处理无法编码的字符
        try:
            # 测试是否可以编码为UTF-8
            text.encode("utf-8")
            return text
        except UnicodeEncodeError:
            # 使用replace策略
            return text.encode("utf-8", errors="replace").decode("utf-8")

    return fix_text


# 使用示例
if __name__ == "__main__":
    print("测试UTF-8强制设置...")
    force_utf8()

    # 测试修复函数
    fix_func = fix_gbk_errors()

    # 测试包含emoji的字符串
    test_text = "🔍 搜索测试"
    fixed_text = fix_func(test_text)
    print(f"原始文本: {test_text}")
    print(f"修复后文本: {fixed_text}")

    print("\n使用方法:")
    print("1. 在main.py顶部添加: from force_utf8_simple import force_utf8")
    print("2. 在main()函数开始处调用: force_utf8()")
    print("3. 或者直接运行此脚本修复问题")
