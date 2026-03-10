# -*- coding: utf-8 -*-
"""
查找剩余的emoji字符
"""

import os
import re


def find_emoji_in_file(filepath):
    """查找文件中的emoji"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 查找非ASCII字符
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # 检查是否有emoji（非ASCII字符）
            non_ascii = []
            for char in line:
                try:
                    char.encode("ascii")
                except UnicodeEncodeError:
                    non_ascii.append(char)

            if non_ascii:
                # 打印文件和行号
                print(f"{filepath}:{i} - {repr(non_ascii)}")
                print(f"  Line: {line}")
                return True

        return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False


def main():
    """主函数"""
    print("Searching for remaining emoji characters...")

    # 检查所有Python文件
    for root, dirs, files in os.walk("."):
        # 跳过某些目录
        if "__pycache__" in root or ".git" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                find_emoji_in_file(filepath)

    print("\nDone!")


if __name__ == "__main__":
    main()
