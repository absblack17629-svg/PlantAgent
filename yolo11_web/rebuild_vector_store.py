# -*- coding: utf-8 -*-
"""
重建 RAG 向量存储 - 清理旧数据，只保留农业知识
"""

import asyncio
import os
import shutil
from yoloapp.rag import RAGService, get_rice_disease_document


async def rebuild_vector_store():
    """重建向量存储"""
    print("=" * 60)
    print("重建 RAG 向量存储")
    print("=" * 60)
    
    try:
        # 1. 删除旧的向量存储
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"\n1️⃣ 删除旧的向量存储: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("✅ 旧向量存储已删除")
        else:
            print(f"\n1️⃣ 向量存储不存在，将创建新的")
        
        # 2. 创建新的 RAG 服务
        print("\n2️⃣ 初始化新的 RAG 服务...")
        rag_service = RAGService()
        await rag_service.init_async()
        
        if not rag_service._initialized:
            print("❌ RAG 服务初始化失败")
            return False
        
        print("✅ RAG 服务初始化成功")
        print(f"   向量存储路径: {os.path.abspath(vector_store_path)}")
        
        # 3. 验证向量存储内容
        print("\n3️⃣ 验证向量存储内容...")
        if rag_service.vector_store:
            # 测试检索
            test_questions = [
                "细菌性条斑病的症状",
                "稻瘟病防治方法",
                "褐斑病发病条件"
            ]
            
            retriever = rag_service.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            for question in test_questions:
                print(f"\n测试问题: {question}")
                docs = await retriever.ainvoke(question)
                print(f"检索到 {len(docs)} 个文档片段")
                
                for i, doc in enumerate(docs, 1):
                    content_preview = doc.page_content[:100].replace('\n', ' ')
                    source = doc.metadata.get('source', 'unknown')
                    print(f"  片段 {i} (来源: {source}): {content_preview}...")
                    
                    # 检查是否有不相关的内容
                    if source == "agent_interaction":
                        print("  ⚠️ 警告: 检测到对话历史数据，应该只包含农业知识")
        
        print("\n" + "=" * 60)
        print("✅ 向量存储重建完成！")
        print("=" * 60)
        print("\n现在可以测试 RAG 检索:")
        print("python diagnose_rag_retrieval.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 重建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(rebuild_vector_store())
