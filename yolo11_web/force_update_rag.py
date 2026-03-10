#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制更新RAG配置
"""

import asyncio
import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def force_update_rag():
    """强制更新RAG配置"""
    print("强制更新RAG配置...")

    try:
        # 1. 检查当前配置
        print("检查当前配置...")

        from config import RAG_CONFIG

        print(f"当前嵌入模型配置: {RAG_CONFIG.get('embedding_model')}")

        # 2. 直接修改RAG_CONFIG
        RAG_CONFIG["embedding_model"] = "BAAI/bge-small-zh-v1.5"
        RAG_CONFIG["offline_mode"] = False  # 使用在线模型

        print(f"更新后嵌入模型配置: {RAG_CONFIG.get('embedding_model')}")

        # 3. 删除向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"删除向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)

        # 4. 重置RAG服务
        from yoloapp.rag import _rag_service_instance

        _rag_service_instance = None
        print("RAG服务已重置")

        # 5. 重新初始化
        print("重新初始化RAG...")
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("RAG重新初始化成功")

            # 6. 测试新模型
            print("\n测试新嵌入模型...")

            # 检查嵌入模型名称
            if hasattr(rag_service.embeddings, "model_name"):
                print(f"实际使用的模型: {rag_service.embeddings.model_name}")
            else:
                print("无法获取模型名称")

            # 测试嵌入
            test_text = "水稻病害防治"
            import asyncio

            loop = asyncio.get_event_loop()

            def embed_query():
                return rag_service.embeddings.embed_query(test_text)

            embedding = await loop.run_in_executor(None, embed_query)
            print(f"嵌入向量维度: {len(embedding)}")

            return True
        else:
            print("RAG重新初始化失败")
            return False

    except Exception as e:
        print(f"强制更新失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_with_simple_query():
    """使用简单查询测试"""
    print("\n使用简单查询测试RAG...")

    try:
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()

        # 创建简单检索器，不使用LLM
        if rag_service.vector_store:
            retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 3})

            # 简单测试查询
            simple_queries = ["稻瘟病", "种植", "灌溉", "施肥", "病虫害"]

            for query in simple_queries:
                print(f"\n查询: {query}")
                docs = await retriever.ainvoke(query)

                if docs:
                    print(f"检索到 {len(docs)} 个文档")

                    for i, doc in enumerate(docs):
                        content = doc.page_content
                        lines = content.splitlines()
                        identifier = ""

                        for line in lines[:3]:
                            if line.strip():
                                identifier = line[:60]
                                break

                        print(f"  文档 {i + 1}: {identifier}...")
                else:
                    print("未检索到文档")

            return True
        else:
            print("向量数据库未初始化")
            return False

    except Exception as e:
        print(f"简单查询测试失败: {e}")
        return False


async def create_direct_rag_test():
    """直接创建RAG测试"""
    print("\n直接创建RAG测试...")

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from yoloapp.rag import get_rice_disease_document

        # 1. 直接使用中文优化模型
        print("加载中文优化嵌入模型...")
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # 2. 加载知识文档
        print("加载知识文档...")
        doc_content = get_rice_disease_document()

        documents = [
            Document(
                page_content=doc_content,
                metadata={
                    "source": "rice_disease_manual",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        # 3. 分割文档
        print("分割文档...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"分割成 {len(split_docs)} 个片段")

        # 4. 创建向量数据库
        print("创建向量数据库...")
        vector_store = FAISS.from_documents(split_docs, embeddings)

        # 5. 测试检索
        print("\n测试检索...")
        retriever = vector_store.as_retriever(search_kwargs={"k": 2})

        test_queries = ["稻瘟病症状", "种植密度", "灌溉方法"]

        for query in test_queries:
            print(f"\n查询: {query}")
            docs = retriever.invoke(query)

            if docs:
                print(f"检索到 {len(docs)} 个文档")

                for i, doc in enumerate(docs):
                    content_preview = doc.page_content[:80].replace("\n", " ")
                    print(f"  文档 {i + 1}: {content_preview}...")
            else:
                print("未检索到文档")

        # 6. 保存向量数据库
        print("\n保存向量数据库...")
        vector_store_path = "./vector_store_direct"
        vector_store.save_local(vector_store_path)
        print(f"向量数据库已保存到: {vector_store_path}")

        return True

    except Exception as e:
        print(f"直接创建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("RAG配置强制更新")
    print("=" * 60)

    # 方法1: 强制更新配置
    print("方法1: 强制更新配置...")
    update_ok = await force_update_rag()

    if update_ok:
        print("\n配置更新成功，测试检索...")
        test_ok = await test_with_simple_query()
    else:
        print("\n配置更新失败")
        test_ok = False

    # 如果方法1失败，使用方法2
    if not test_ok:
        print("\n" + "=" * 60)
        print("方法1失败，尝试方法2: 直接创建RAG...")

        direct_ok = await create_direct_rag_test()

        if direct_ok:
            print("\n直接创建成功！")
            print(
                "注意: 需要将向量数据库从 ./vector_store_direct 移动到 ./vector_store"
            )
        else:
            print("\n直接创建失败")

    print("\n" + "=" * 60)
    print("操作完成")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"\n操作失败: {e}")
