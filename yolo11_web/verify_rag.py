#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证RAG系统
"""

import os
import sys


def check_document():
    """检查文档"""
    print("检查RAG文档...")

    try:
        # 直接读取文档函数
        with open("yoloapp/rag.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 找到函数定义
        func_def = "def get_rice_disease_document():"
        start = content.find(func_def)

        if start == -1:
            print("未找到文档函数")
            return False

        # 找到函数结束
        end = content.find("\ndef ", start + len(func_def))
        if end == -1:
            end = len(content)

        # 提取函数内容
        func_content = content[start:end].strip()

        # 检查函数返回值

        if 'return """' in func_content:
            print("文档函数正常")
            return True
        else:
            print("文档函数可能有问题")
            return False

    except Exception as e:
        print(f"检查失败: {e}")
        return False


def check_vector_store():
    """检查向量数据库"""
    print("\n检查向量数据库...")

    vector_store_path = "./vector_store"

    if os.path.exists(vector_store_path):
        files = os.listdir(vector_store_path)
        print(f"向量数据库目录: {vector_store_path}")
        print(f"包含文件: {files}")
        return True
    else:
        print("向量数据库不存在")
        return False


def check_llm_config():
    """检查LLM配置"""
    print("\n检查LLM配置...")

    # 检查.env文件
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            env_content = f.read()

        # 检查关键配置

        required_keys = ["ZHIPU_MODEL", "ZHIPU_BASE_URL", "ZHIPU_API_KEY"]

        for key in required_keys:
            if f"{key}=" in env_content:
                print(f"{key}: 已设置")
            else:
                print(f"{key}: 未设置")
                return False

        return True

    else:
        print(".env文件不存在")
        return False


def create_quick_test():
    """创建快速测试"""
    print("\n创建快速测试...")

    test_code = '''#!/usr/bin/env python3
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
    
    print("\n" + "=" * 60)
    print("[OK] RAG系统基本可用")
    print("\n下一步建议:")
    print("  1. 启动服务: python main.py")
    print("  2. 测试检测功能: 上传水稻病害图片")
    print("  3. 验证三选项确认流程")
    print("  4. 检查RAG回答质量")
    
    return True

if __name__ == "__main__":
    quick_check()
'''

    with open("quick_rag_check.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    print("快速测试已创建: quick_rag_check.py")
    return True


def main():
    """主函数"""
    print("验证RAG系统")
    print("=" * 60)

    # 1. 检查文档
    doc_ok = check_document()

    # 2. 检查向量数据库
    vector_ok = check_vector_store()

    # 3. 检查配置
    config_ok = check_llm_config()

    # 4. 创建快速测试
    create_quick_test()

    print("\n" + "=" * 60)
    print("验证完成！")

    overall = doc_ok and vector_ok and config_ok

    if overall:
        print("[OK] RAG系统基本可用")
        print("\n运行快速检查:")
        print("  python quick_rag_check.py")
    else:
        print("[WARNING] RAG系统可能存在一些问题")

    return overall


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"验证失败: {e}")
        sys.exit(1)
