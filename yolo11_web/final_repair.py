#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终修复：恢复RAG系统功能
"""

import os
import sys


def repair_rag_file():
    """修复RAG文件"""
    print("修复RAG文件...")

    rag_file = "yoloapp/rag.py"

    # 1. 读取优化后的文档
    with open("optimized_rice_knowledge.txt", "r", encoding="utf-8") as f:
        optimized_doc = f.read()

    # 2. 读取RAG文件
    with open(rag_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. 找到get_rice_disease_document函数并替换
    # 查找函数开始位置
    func_start = content.find("def get_rice_disease_document():")
    if func_start == -1:
        print("未找到get_rice_disease_document函数")
        return False

    # 查找函数结束位置（下一个def或文件结束）
    func_end = content.find("\ndef ", func_start + 1)
    if func_end == -1:
        func_end = len(content)

    # 创建新的函数内容
    new_function = (
        '''def get_rice_disease_document():
    """获取水稻病害知识文档"""
    return """'''
        + optimized_doc
        + '"""\n\n'
    )

    # 替换函数
    new_content = content[:func_start] + new_function + content[func_end:]

    # 4. 写回文件
    with open(rag_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("RAG文件已修复")
    return True


def verify_rag_file():
    """验证RAG文件"""
    print("\n验证RAG文件...")

    try:
        # 尝试导入以验证语法
        rag_file = "yoloapp/rag.py"

        with open(rag_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否有语法错误
        import ast

        ast.parse(content)

        print("RAG文件语法正确")
        return True

    except SyntaxError as e:
        print(f"RAG文件语法错误: {e}")
        return False
    except Exception as e:
        print(f"验证失败: {e}")
        return False


def create_simple_test():
    """创建简单测试"""
    print("\n创建简单测试...")

    test_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单RAG测试
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test():
    """测试函数"""
    try:
        from yoloapp.rag import get_rice_disease_document
        
        # 测试文档获取
        doc = get_rice_disease_document()
        print(f"文档长度: {len(doc)} 字符")
        
        # 检查关键内容
        if "稻瘟病" in doc and "种植密度" in doc and "灌溉策略" in doc:
            print("文档包含关键内容")
            return True
        else:
            print("文档可能不完整")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
'''

    with open("test_rag_simple2.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    print("简单测试已创建: test_rag_simple2.py")
    return True


def main():
    """主函数"""
    print("最终修复：恢复RAG系统功能")
    print("=" * 60)

    # 1. 修复RAG文件
    if not repair_rag_file():
        print("修复失败")
        return False

    # 2. 验证文件
    if not verify_rag_file():
        print("验证失败")
        return False

    # 3. 创建测试
    create_simple_test()

    print("\n" + "=" * 60)
    print("修复完成！")
    print("\n下一步:")
    print("  1. 运行测试: python test_rag_simple2.py")
    print("  2. 测试RAG系统: python check_status.py")
    print("  3. 运行完整功能测试: python 快速功能测试.py")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"修复失败: {e}")
        sys.exit(1)
