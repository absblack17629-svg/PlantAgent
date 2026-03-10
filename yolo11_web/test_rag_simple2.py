#!/usr/bin/env python3
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
