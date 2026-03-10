#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查向量数据库内容
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def check_vector_store():
    """检查向量数据库"""
    print("检查向量数据库内容...")

    try:
        from yoloapp.rag import get_rag_service

        # 初始化RAG
        rag_service = get_rag_service()
        await rag_service.initialize()

        if not rag_service.vector_store:
            print("向量数据库未初始化")
            return

        # 获取所有文档
        print("\n向量数据库统计:")

        # 尝试不同的检索方式
        test_queries = [
            "稻瘟病症状",
            "种植密度规划",
            "灌溉策略",
            "施肥管理",
            "病虫害防治",
            "收获储存",
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 3})

            try:
                docs = await retriever.ainvoke(query)
                print(f"  检索到 {len(docs)} 个文档")

                for i, doc in enumerate(docs):
                    source = doc.metadata.get("source", "unknown")
                    content_preview = doc.page_content[:100].replace("\n", " ")
                    print(f"  文档 {i + 1}:")
                    print(f"    来源: {source}")
                    print(f"    内容: {content_preview}...")

                    # 检查内容是否相关
                    if any(
                        keyword in content_preview
                        for keyword in ["稻瘟", "种植", "灌溉", "施肥", "病虫", "收获"]
                    ):
                        print(f"    [相关] 包含关键词")
                    else:
                        print(f"    [可能不相关]")

            except Exception as e:
                print(f"  检索失败: {e}")

        # 检查向量数据库大小
        print("\n向量数据库详细信息:")

        # 尝试获取索引信息
        try:
            # FAISS索引信息
            index = rag_service.vector_store.index
            print(f"向量维度: {index.d}")
            print(f"向量数量: {index.ntotal}")
        except Exception as e:
            print(f"无法获取索引信息: {e}")

    except Exception as e:
        print(f"检查失败: {e}")
        import traceback

        traceback.print_exc()


async def rebuild_vector_store():
    """重建向量数据库"""
    print("\n重建向量数据库...")

    try:
        import shutil

        vector_store_path = "./vector_store"

        # 删除现有目录
        if os.path.exists(vector_store_path):
            shutil.rmtree(vector_store_path)
            print("已删除旧的向量数据库")

        # 重置RAG服务
        from yoloapp.rag import _rag_service_instance

        _rag_service_instance = None

        # 重新初始化
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("向量数据库重建成功")
            return True
        else:
            print("向量数据库重建失败")
            return False

    except Exception as e:
        print(f"重建失败: {e}")
        return False


async def check_document_splitting():
    """检查文档分割"""
    print("\n检查文档分割...")

    try:
        from yoloapp.rag import get_rice_disease_document
        from yoloapp.rag import RAGService
        from langchain_core.documents import Document
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # 获取文档
        doc_content = get_rice_disease_document()

        # 创建文档对象
        documents = [
            Document(
                page_content=doc_content,
                metadata={
                    "source": "rice_disease_manual",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        # 使用相同的分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        split_docs = text_splitter.split_documents(documents)

        print(f"原始文档分割成 {len(split_docs)} 个片段")

        # 显示片段内容
        for i, doc in enumerate(split_docs[:5]):  # 只显示前5个
            content = doc.page_content
            lines = content.splitlines()
            print(f"\n片段 {i + 1} (长度: {len(content)} 字符):")
            print(f"前3行: {lines[0][:80]}...")
            if len(lines) > 1:
                print(f"       {lines[1][:80]}...")
            if len(lines) > 2:
                print(f"       {lines[2][:80]}...")

        return len(split_docs)

    except Exception as e:
        print(f"检查文档分割失败: {e}")
        return 0


async def main():
    """主函数"""
    print("=== 向量数据库检查 ===")

    # 检查文档分割
    num_chunks = await check_document_splitting()

    if num_chunks < 5:
        print(f"\n警告: 文档只分割成 {num_chunks} 个片段，可能太少")

    # 检查向量数据库
    await check_vector_store()

    # 询问是否重建
    print("\n" + "=" * 60)
    response = input("是否重建向量数据库？(y/n): ")

    if response.lower() == "y":
        if await rebuild_vector_store():
            print("\n重新检查向量数据库...")
            await check_vector_store()

    print("\n=== 检查完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
