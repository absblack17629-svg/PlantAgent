# -*- coding: utf-8 -*-
"""
修复 Windows GBK 编码问题 - 移除或替换 emoji 字符
"""

import os
import sys
import re

# 强制使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Emoji 替换映射
EMOJI_REPLACEMENTS = {
    '✅': '[OK]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '📊': '[STATS]',
    '🔍': '[SEARCH]',
    '💡': '[INFO]',
    '📦': '[BOX]',
    '🎯': '[TARGET]',
    '📍': '[LOCATION]',
    '🔄': '[PROGRESS]',
    '💧': '[WATER]',
}

def remove_emojis_from_file(filepath):
    """从文件中移除或替换 emoji"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换已知的 emoji
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] 已修复: {filepath}")
            return True
        
        return False
    
    except Exception as e:
        print(f"[FAIL] 处理文件失败 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始修复 Windows GBK 编码问题...")
    print("=" * 60)
    
    # 需要检查的目录
    directories = [
        'services',
        'routers',
        'yoloapp',
        'skills',
    ]
    
    fixed_count = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        print(f"\n检查目录: {directory}/")
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    if remove_emojis_from_file(filepath):
                        fixed_count += 1
    
    print("\n" + "=" * 60)
    print(f"修复完成! 共修复 {fixed_count} 个文件")
    print("=" * 60)
    
    # 验证关键文件
    print("\n验证关键文件...")
    key_files = [
        'services/detection_service.py',
        'routers/agent_factory.py',
    ]
    
    for filepath in key_files:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_emoji = any(emoji in content for emoji in EMOJI_REPLACEMENTS.keys())
            
            if has_emoji:
                print(f"[WARN] {filepath} 仍包含 emoji")
            else:
                print(f"[OK] {filepath} 已清理")

if __name__ == "__main__":
    main()
