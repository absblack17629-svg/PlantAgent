#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找所有包含Unicode字符的print语句
"""

import os
import sys


def check_file(filepath):
    """检查文件中的Unicode print语句"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            if "print" in line:
                # 检查是否包含非ASCII字符
                for char in line:
                    if ord(char) > 127:
                        print(f"{filepath}:{i} - {line.strip()}")
                        return True
    except Exception as e:
        pass
    return False


def main():
    """主函数"""
    print("查找所有包含Unicode字符的print语句...")

    files_to_check = [
        "services/detection_service.py",
        "services/enhanced_detection_service.py",
        "yoloapp/tool/detection_tool.py",
        "yoloapp/agent/detection_agent.py",
        "skills/detection_skill.py",
    ]

    found = False
    for filepath in files_to_check:
        if os.path.exists(filepath):
            if check_file(filepath):
                found = True

    if not found:
        print("没有找到包含Unicode字符的print语句")

    # 检查其他可能的地方
    print("\n检查其他可能的地方...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                # 跳过一些目录
                if "__pycache__" in filepath or ".git" in filepath:
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        if "print" in content and any(ord(c) > 127 for c in content):
                            # 检查是否是表情符号
                            for char in content:
                                if ord(char) > 127 and "print" in content:
                                    lines = content.split("\n")
                                    for i, line in enumerate(lines, 1):
                                        if "print" in line and char in line:
                                            print(
                                                f"{filepath}:{i} - {line.strip()[:100]}"
                                            )
                                            break
                                    break
                except:
                    pass


if __name__ == "__main__":
    main()
