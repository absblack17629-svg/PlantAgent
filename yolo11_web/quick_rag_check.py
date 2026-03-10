#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速RAG系统状态检查
"""

import os

def quick_check():
    """快速检查"""
    print("RAG系统状态检查")
    print("=" * 60)
    
    # 1. 检查向量数据库
    vector_store_path = "./vector_store"
    if os.path.exists(vector_store_path):
        print("[OK] 向量数据库存在")
        files = os.listdir(vector_store_path)
        print(f"   目录内容: {files}")
    else:
        print("[ERROR] 向量数据库不存在")
        return False
    
    # 2. 检查关键文件

    required_files = [
        "yoloapp/rag.py",
        "yoloapp/llm.py",
        "config/settings.py",
        ".env"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file} 存在")
        else:
            print(f"[ERROR] {file} 不存在")
            return False
    
    # 3. 检查知识文档
    try:
        import ast
        
        with open("yoloapp/rag.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 解析语法

        ast.parse(content)
        print("[OK] RAG文件语法正确")
        
        # 检查文档函数

        if "def get_rice_disease_document():" in content and 'return """' in content:
            print("[OK] 文档函数正常")
        else:
            print("[ERROR] 文档函数可能有问题")
            return False
        
    except SyntaxError as e:
        print(f"[ERROR] RAG文件语法错误: {e}")
        return False
    
    # 4. 检查配置
    try:
        with open(".env", "r", encoding="utf-8") as f:
            env_content = f.read()
        
        if "deepseek-v3.2" in env_content and "ark.cn-beijing.volces.com" in env_content:
            print("[OK] DeepSeek-v3.2配置正确")
        else:
            print("[WARNING] 配置可能不是DeepSeek-v3.2")
    
    except Exception as e:
        print(f"[WARNING] 配置检查失败: {e}")
    
    print("
" + "=" * 60)
    print("[OK] RAG系统基本可用")
    print("
下一步建议:")
    print("  1. 启动服务: python main.py")
    print("  2. 测试检测功能: 上传水稻病害图片")
    print("  3. 验证三选项确认流程")
    print("  4. 检查RAG回答质量")
    
    return True

if __name__ == "__main__":
    quick_check()
