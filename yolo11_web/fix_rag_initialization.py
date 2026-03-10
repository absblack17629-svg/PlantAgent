# -*- coding: utf-8 -*-
"""
修复RAG系统初始化问题
"""

import asyncio
import os
import sys

async def main():
    print("=" * 60)
    print("修复RAG系统初始化")
    print("=" * 60)
    
    try:
        # 1. 检查向量存储是否存在
        vector_store_path = "./vector_store"
        if not os.path.exists(vector_store_path):
            print(f"\n[WARN] 向量存储不存在: {vector_store_path}")
            print("[INFO] 需要重建向量存储...")
            print("\n运行以下命令:")
            print("  python rebuild_vector_store.py")
            return False
        
        print(f"\n[OK] 向量存储存在: {vector_store_path}")
        
        # 2. 检查嵌入模型
        embedding_model = "./bge-small-zh-v1.5"
        if not os.path.exists(embedding_model):
            print(f"\n[WARN] 嵌入模型不存在: {embedding_model}")
            print("[INFO] 请确保模型文件已下载到该位置")
            return False
        
        print(f"\n[OK] 嵌入模型存在: {embedding_model}")
        
        # 3. 尝试初始化RAG服务
        print("\n[INFO] 尝试初始化RAG服务...")
        from yoloapp.rag import RAGService
        
        rag_service = RAGService()
        await rag_service.init_async()
        
        if rag_service._initialized:
            print("[SUCCESS] RAG服务初始化成功")
            
            # 4. 测试查询
            print("\n[INFO] 测试RAG查询...")
            from yoloapp.llm import get_llm_client
            
            llm = get_llm_client()
            result = await rag_service.query("稻瘟病的防治方法", llm)
            
            if result and "暂未初始化" not in result:
                print(f"[SUCCESS] RAG查询成功: {result[:100]}...")
                return True
            else:
                print(f"[WARN] RAG查询返回: {result}")
                return False
        else:
            print("[FAILURE] RAG服务初始化失败")
            return False
            
    except Exception as e:
        print(f"[FAILURE] 修复过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
