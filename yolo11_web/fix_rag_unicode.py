#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复RAG文件中的Unicode字符
"""

import re


def fix_rag_file():
    """修复RAG文件中的Unicode字符"""
    filepath = "yoloapp/rag.py"

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 替换Unicode表情符号为文本
    replacements = {
        "[DETECT]": "[SEARCH]",
        "[OK]": "[OK]",
        "[WARNING]": "[WARN]",
        "[ERROR]": "[ERROR]",
        "[TIP]": "[TIP]",
        "[ROBOT]": "[AI]",
        "[FOLDER]": "[FILE]",
        "[NET]": "[NET]",
        "[DELETE]": "[DELETE]",
        "[REFRESH_CW]": "[RELOAD]",
        "[DOC]": "[DOC]",
        "[NOTE]": "[NOTE]",
        "[CELEBRATE]": "[CELEBRATE]",
    }

    for unicode_char, text in replacements.items():
        content = content.replace(unicode_char, text)

    # 保存修复后的文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"已修复文件: {filepath}")

    # 也修复LLM文件
    filepath2 = "yoloapp/llm.py"
    with open(filepath2, "r", encoding="utf-8") as f:
        content2 = f.read()

    for unicode_char, text in replacements.items():
        content2 = content2.replace(unicode_char, text)

    with open(filepath2, "w", encoding="utf-8") as f:
        f.write(content2)

    print(f"已修复文件: {filepath2}")


if __name__ == "__main__":
    fix_rag_file()
