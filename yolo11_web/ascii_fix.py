# -*- coding: utf-8 -*-
"""
ASCII安全修复脚本 - 完全使用ASCII字符
"""

import os

# 只修复最关键的几个文件
CRITICAL_FILES = [
    "services/detection_service.py",
    "yoloapp/rag.py",
    "yoloapp/flow/nine_node_graph.py",
    "yoloapp/flow/nine_node_with_tools.py",
    "yoloapp/flow/knowledge_flow.py",
]

# 简单的emoji替换映射
EMOJI_MAP = {
    "\U0001f50d": "[SEARCH]",  # 🔍
    "\u2705": "[SUCCESS]",     # ✅
    "\u274c": "[FAILURE]",     # ❌
    "\u26a0\ufe0f": "[WARNING]",  # ⚠️
    "\U0001f4ca": "[STATS]",   # 📊
    "\U0001f4c8": "[UP]",      # 📈
    "\U0001f4c9": "[DOWN]",    # 📉
    "\U0001f4c1": "[FILE]",    # 📁
    "\U0001f4dd": "[DETAIL]",  # 📝
}

def fix_file(filepath):
    """修复单个文件"""
    if not os.path.exists(filepath):
        print("文件不存在: " + filepath)
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changed = False
        for emoji, replacement in EMOJI_MAP.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changed = True
                print("  - 替换 " + replacement)
        
        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print("已修复: " + filepath)
            return True
        else:
            print("无需修复: " + filepath)
            return False
    
    except Exception as e:
        print("修复失败 " + filepath + ": " + str(e))
        return False

def main():
    print("快速修复核心emoji问题...")
    print("只修复导致API错误的文件")
    print("="*50)
    
    fixed_count = 0
    for filepath in CRITICAL_FILES:
        print("\n检查: " + filepath)
        if fix_file(filepath):
            fixed_count += 1
    
    print("\n修复完成: " + str(fixed_count) + "/" + str(len(CRITICAL_FILES)) + " 个文件已修复")
    
    if fixed_count > 0:
        print("\n现在API应该可以正常工作了")
        print("运行测试: python test_real_api.py")

if __name__ == "__main__":
    main()