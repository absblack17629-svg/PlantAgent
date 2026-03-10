# -*- coding: utf-8 -*-
"""
快速修复核心emoji问题 - 只修复导致API错误的文件
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
    "🔍": "[SEARCH]",
    "✅": "[SUCCESS]",
    "❌": "[FAILURE]",
    "⚠️": "[WARNING]",
    "📊": "[STATS]",
}

def fix_file(filepath):
    """修复单个文件"""
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        changed = False
        for emoji, replacement in EMOJI_MAP.items():
            if emoji in content:
                content = content.replace(emoji, replacement)
                changed = True
                print(f"  - 替换 {emoji} → {replacement}")
        
        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {filepath}")
            return True
        else:
            print(f"✅ 无需修复: {filepath}")
            return False
    
    except Exception as e:
        print(f"❌ 修复失败 {filepath}: {e}")
        return False

def main():
    print("快速修复核心emoji问题...")
    print("只修复导致API错误的文件")
    print("="*50)
    
    fixed_count = 0
    for filepath in CRITICAL_FILES:
        print(f"\n检查: {filepath}")
        if fix_file(filepath):
            fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{len(CRITICAL_FILES)} 个文件已修复")
    
    if fixed_count > 0:
        print("\n现在API应该可以正常工作了")
        print("运行测试: python test_real_api.py")

if __name__ == "__main__":
    main()