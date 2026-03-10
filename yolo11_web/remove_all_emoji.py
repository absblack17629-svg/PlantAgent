# -*- coding: utf-8 -*-
"""
移除所有emoji表情，替换为纯文本
"""

import os
import re
import sys

# emoji到纯文本的映射
EMOJI_REPLACEMENTS = {
    # 常用状态emoji
    "[START]": "[START]",
    "[OK]": "[OK]",
    "[HOT]": "[HOT]",
    "[PACKAGE]": "[PACKAGE]",
    "[CELEBRATE]": "[CELEBRATE]",
    "[WARN]": "[WARN]",
    "[ERROR]": "[ERROR]",
    "[SPARKLE]": "[SPARKLE]",
    "[IDEA]": "[IDEA]",
    "[STOP]": "[STOP]",
    "[SEARCH]": "[SEARCH]",
    "[SEARCH]": "[SEARCH]",
    "[TOOL]": "[TOOL]",
    "[TARGET]": "[TARGET]",
    "[BOOK]": "[BOOK]",
    "[MAP]": "[MAP]",
    "[QUESTION]": "[QUESTION]",
    "[CHAT]": "[CHAT]",
    "[WAITING]": "[WAITING]",
    "[MICROSCOPE]": "[MICROSCOPE]",
    # 农业相关emoji
    "[RICE]": "[RICE]",
    "[WATER]": "[WATER]",
    "[SEEDLING]": "[SEEDLING]",
    "[RAIN]": "[RAIN]",
    "[SUNNY]": "[SUNNY]",
    "[THERMOMETER]": "[THERMOMETER]",
    "[MEDICINE]": "[MEDICINE]",
    "[PROTECT]": "[PROTECT]",
    # 其他常见emoji
    "[TEST]": "[TEST]",
    "[ROBOT]": "[ROBOT]",
    "[NET]": "[NET]",
    "[DELETE]": "[DELETE]",
    "[DOC]": "[DOC]",
    "[SPIDER]": "[SPIDER]",
    "[ALERT]": "[ALERT]",
    "[TOOLBOX]": "[TOOLBOX]",
    "[THINK]": "[THINK]",
    "[FINISH]": "[FINISH]",
    "[CLEAN]": "[CLEAN]",
    "[CLEAN]": "[CLEAN]",
    "[FAST]": "[FAST]",
    "[CAMERA]": "[CAMERA]",
    "[CAMERA]": "[CAMERA]",
    "[KEY]": "[KEY]",
    "[PYTHON]": "[PYTHON]",
    "[PENGUIN]": "[PENGUIN]",
    "[USER]": "[USER]",
}


def replace_emoji_in_file(filepath):
    """替换文件中的emoji"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 替换所有emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)

        # 如果内容有变化，保存文件
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"  处理文件失败 {filepath}: {e}")
        return False


def process_directory(directory):
    """处理目录中的所有Python文件"""
    print(f"处理目录: {directory}")

    changed_files = []

    for root, dirs, files in os.walk(directory):
        # 跳过某些目录
        if "__pycache__" in root or ".git" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                print(f"  检查: {filepath}")

                if replace_emoji_in_file(filepath):
                    changed_files.append(filepath)

    return changed_files


def main():
    """主函数"""
    print("开始移除所有emoji表情...")

    # 处理当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    changed_files = process_directory(current_dir)

    print(f"\n处理完成！修改了 {len(changed_files)} 个文件:")
    for file in changed_files:
        print(f"  {file}")

    # 创建修复后的测试
    print("\n创建修复后的测试...")
    test_code = '''# -*- coding: utf-8 -*-
"""
修复后的测试 - 纯文本无emoji
"""

print("[START] 测试开始")
print("[OK] 测试通过")
print("[ERROR] 测试失败")
print("[WARN] 警告信息")
print("[SEARCH] 搜索中...")
print("[FINISH] 测试完成")
'''

    test_file = os.path.join(current_dir, "test_no_emoji.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_code)

    print(f"创建测试文件: {test_file}")

    # 运行测试
    print("\n运行测试...")
    os.system(f'python "{test_file}"')


if __name__ == "__main__":
    main()
