# -*- coding: utf-8 -*-
"""
批量修复emoji字符 - 将emoji替换为文本表示
解决Windows GBK编码问题
"""

import os
import re
import glob

# emoji到文本的映射
EMOJI_MAPPING = {
    # 状态emoji
    "✅": "[SUCCESS]",
    "❌": "[FAILURE]",
    "⚠️": "[WARNING]",
    "🔍": "[SEARCH]",
    "🚀": "[RUN]",
    "📊": "[STATS]",
    "📈": "[UP]",
    "📉": "[DOWN]",
    "📁": "[FILE]",
    "📝": "[DETAIL]",
    "🎉": "[CELEBRATE]",
    "🔧": "[FIX]",
    "🔨": "[TOOL]",
    "💡": "[IDEA]",
    "✨": "[SPARKLE]",
    "🌟": "[STAR]",
    "🔥": "[FIRE]",
    "💥": "[BLAST]",
    "💣": "[BOMB]",
    "💀": "[SKULL]",
    "👀": "[EYES]",
    "👁️": "[EYE]",
    "👁‍🗨": "[EYE_SPEECH]",
    "🧠": "[BRAIN]",
    "💪": "[MUSCLE]",
    "🦾": "[MECHANICAL_ARM]",
    "🦿": "[MECHANICAL_LEG]",
    "🦵": "[LEG]",
    "🦶": "[FOOT]",
    "👂": "[EAR]",
    "👃": "[NOSE]",
    "👄": "[MOUTH]",
    "👅": "[TONGUE]",
    "🧑": "[PERSON]",
    "👤": "[BUST]",
    "👥": "[BUSTS]",
    "🗣️": "[SPEAKING_HEAD]",
    "👶": "[BABY]",
    "🧒": "[CHILD]",
    "👦": "[BOY]",
    "👧": "[GIRL]",
    "🧑": "[ADULT]",
    "👨": "[MAN]",
    "👩": "[WOMAN]",
    "🧓": "[OLDER_ADULT]",
    "👴": "[OLD_MAN]",
    "👵": "[OLD_WOMAN]",
}


def fix_emoji_in_file(filepath):
    """修复单个文件中的emoji字符"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changed = False

        # 替换所有emoji字符
        for emoji, replacement in EMOJI_MAPPING.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changed = True

        # 如果有变化，保存文件
        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"已修复: {filepath}")
            return True
        else:
            return False

    except Exception as e:
        print(f"修复失败 {filepath}: {e}")
        return False


def find_python_files_with_emoji():
    """查找包含emoji的Python文件"""
    python_files = glob.glob("**/*.py", recursive=True)

    emoji_files = []
    for filepath in python_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否包含emoji
            for emoji in EMOJI_MAPPING.keys():
                if emoji in content:
                    emoji_files.append(filepath)
                    break

        except Exception as e:
            print(f"读取失败 {filepath}: {e}")

    return emoji_files


def main():
    """主函数"""
    print("搜索包含emoji的Python文件...")
    emoji_files = find_python_files_with_emoji()

    if not emoji_files:
        print("未找到包含emoji的Python文件")
        return

    print(f"找到 {len(emoji_files)} 个包含emoji的文件:")
    for filepath in emoji_files:
        print(f"  - {filepath}")

    print("\n开始修复...")
    fixed_count = 0
    for filepath in emoji_files:
        if fix_emoji_in_file(filepath):
            fixed_count += 1

    print(f"\n修复完成: {fixed_count}/{len(emoji_files)} 个文件已修复")

    # 显示修复前后对比
    if fixed_count > 0:
        print("\n修复前后的emoji映射:")
        for emoji, replacement in EMOJI_MAPPING.items():
            print(f"  {emoji} → {replacement}")


if __name__ == "__main__":
    main()
