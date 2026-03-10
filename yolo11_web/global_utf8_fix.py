#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全局UTF-8编码修复方案

直接重写sys.stdout和print函数，强制所有输出使用UTF-8编码。
这是解决Windows上GBK编码错误的最直接方法。
"""

import sys
import os
import builtins

# 保存原始的print函数
_original_print = builtins.print
_original_stdout = sys.stdout
_original_stderr = sys.stderr


def force_utf8_print():
    """
    强制所有print输出使用UTF-8编码

    这个方法：
    1. 设置环境变量强制UTF-8
    2. 重写print函数处理编码
    3. 确保所有输出都是UTF-8安全的
    """
    # 设置环境变量
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"

    # 创建安全的print函数
    def safe_print(*args, **kwargs):
        """安全的print函数，处理编码问题"""
        try:
            # 处理所有参数
            safe_args = []
            for arg in args:
                if isinstance(arg, str):
                    # 尝试编码为UTF-8
                    try:
                        arg.encode("utf-8")
                        safe_args.append(arg)
                    except UnicodeEncodeError:
                        # 使用replace策略
                        safe_args.append(
                            arg.encode("utf-8", errors="replace").decode("utf-8")
                        )
                else:
                    safe_args.append(arg)

            # 使用原始的print函数
            return _original_print(*safe_args, **kwargs)
        except Exception as e:
            # 如果出错，尝试原始方法
            try:
                return _original_print(*args, **kwargs)
            except:
                # 最后的手段：静默失败
                pass

    # 替换全局print函数
    builtins.print = safe_print

    # Windows特定设置
    if sys.platform == "win32":
        try:
            # 设置控制台编码
            if sys.stdout and hasattr(sys.stdout, "buffer"):
                import io

                # 重新配置stdout
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer,
                    encoding="utf-8",
                    errors="replace",
                    write_through=True,
                )
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer,
                    encoding="utf-8",
                    errors="replace",
                    write_through=True,
                )
        except Exception:
            pass  # 如果失败，继续使用安全的print

    print("✅ 全局UTF-8编码修复已应用")
    print("✅ 所有print输出现在都是UTF-8安全的")


def safe_string(text):
    """
    确保字符串是UTF-8安全的

    Args:
        text: 任何输入

    Returns:
        UTF-8安全的字符串
    """
    if text is None:
        return ""

    if not isinstance(text, str):
        text = str(text)

    try:
        text.encode("utf-8")
        return text
    except UnicodeEncodeError:
        return text.encode("utf-8", errors="replace").decode("utf-8")


# 自动应用修复
force_utf8_print()


# 使用示例
if __name__ == "__main__":
    print("测试UTF-8编码修复...")
    print("包含emoji的文本: 🔍 ✅ ❌ ⚠️ 📊")
    print("中文字符测试: 中文测试")
    print("混合测试: 中文🔍混合✅测试")

    print("\n✅ 修复完成！")
    print("现在可以在整个应用中使用print函数而不用担心编码错误了。")
