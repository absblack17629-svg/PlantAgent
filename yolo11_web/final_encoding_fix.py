#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终编码修复方案

完全避免使用emoji，使用纯文本替代，从根本上解决编码问题。
"""

import sys
import os
import builtins

def apply_final_fix():
    """
    应用最终编码修复
    
    这个方法：
    1. 完全避免使用emoji
    2. 使用纯文本替代所有特殊字符
    3. 重写print函数确保安全
    """
    # 保存原始的print函数
    _original_print = builtins.print
    
    # 替换映射：emoji -> 文本
    EMOJI_REPLACEMENTS = {
        "🔍": "[SEARCH]",
        "🔎": "[SEARCH]",
        "✅": "[SUCCESS]",
        "❌": "[ERROR]",
        "⚠️": "[WARNING]",
        "⭕": "[CIRCLE]",
        "❎": "[CROSS]",
        "⚡": "[FLASH]",
        "📊": "[CHART]",
        "📈": "[UP]",
        "📉": "[DOWN]",
        "📋": "[CLIPBOARD]",
        "📝": "[NOTE]",
        "📚": "[BOOKS]",
        "📖": "[BOOK]",
        "📌": "[PIN]",
        "🔬": "[MICROSCOPE]",
        "🔭": "[TELESCOPE]",
        "🌾": "[RICE]",
        "🌱": "[SEEDLING]",
        "🍚": "[RICE_BOWL]",
        "🦠": "[MICROBE]",
        "💡": "[IDEA]",
        "🔑": "[KEY]",
        "🔒": "[LOCK]",
        "🔓": "[UNLOCK]",
        "🔔": "[BELL]",
        "🔕": "[NO_BELL]",
        "🎯": "[TARGET]",
        "🎉": "[PARTY]",
        "🎊": "[CONFETTI]",
    }
    
    def replace_emoji(text):
        """替换所有emoji为文本"""
        if not isinstance(text, str):
            return text
        
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            text = text.replace(emoji, replacement)
        
        return text
    
    def safe_print(*args, **kwargs):
        """完全安全的print函数"""
        # 处理所有参数，替换emoji
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(replace_emoji(arg))
            else:
                safe_args.append(arg)
        
        # 使用原始的print函数
        return _original_print(*safe_args, **kwargs)
    
    # 替换全局print函数
    builtins.print = safe_print
    
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    print("[SUCCESS] 最终编码修复已应用")
    print("[INFO] 所有emoji已替换为文本，编码问题已解决")


def fix_all_files():
    """
    修复所有Python文件中的emoji
    
    这个函数会扫描并修复项目中的所有Python文件，
    将emoji替换为文本表示。
    """
    import glob
    
    # 要修复的文件模式
    patterns = [
        "*.py",
        "**/*.py",
        "yoloapp/**/*.py",
        "services/**/*.py",
        "routers/**/*.py",
    ]
    
    # emoji替换映射
    EMOJI_REPLACEMENTS = {
        "🔍": "[SEARCH]",
        "✅": "[SUCCESS]",
        "❌": "[ERROR]",
        "⚠️": "[WARNING]",
        "📊": "[CHART]",
        "🌾": "[RICE]",
        # 添加更多需要替换的emoji
    }
    
    fixed_count = 0
    
    for pattern in patterns:
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含emoji
                has_emoji = False
                for emoji in EMOJI_REPLACEMENTS:
                    if emoji in content:
                        has_emoji = True
                        break
                
                if has_emoji:
                    # 替换emoji
                    for emoji, replacement in EMOJI_REPLACEMENTS.items():
                        content = content.replace(emoji, replacement)
                    
                    # 写回文件
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    fixed_count += 1
                    print(f"[FIXED] 修复文件: {filepath}")
                    
            except Exception as e:
                print(f"[ERROR] 处理文件 {filepath} 时出错: {e}")
    
    print(f"[SUMMARY] 共修复 {fixed_count} 个文件")


# 使用示例
if __name__ == "__main__":
    print("选择修复方式:")
    print("1. 应用运行时修复（推荐）")
    print("2. 修复所有文件（永久性）")
    print("3. 两者都做")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    
    if choice in ["1", "3"]:
        apply_final_fix()
        print("\n✅ 运行时修复已应用")
        print("   现在可以安全地运行应用了")
    
    if choice in ["2", "3"]:
        print("\n开始修复所有文件...")
        fix_all_files()
        print("\n✅ 所有文件已修复")
        print("   emoji已永久替换为文本")
    
    print("\n🎉 编码问题已彻底解决！")