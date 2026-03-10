#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试嵌入模型
"""

import asyncio
import sys
import os
import numpy as np

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_embeddings():
    """测试嵌入模型"""
    print("测试嵌入模型...")

    try:
        from yoloapp.rag import get_rag_service

        # 初始化RAG
        rag_service = get_rag_service()
        await rag_service.initialize()

        if not rag_service.embeddings:
            print("嵌入模型未初始化")
            return False

        print("嵌入模型已初始化")

        # 测试嵌入
        test_texts = [
            "水稻稻瘟病的症状是什么？",
            "水稻种植密度规划",
            "水稻灌溉策略",
            "收获与储存技术",
        ]

        print("\n生成嵌入向量...")

        # 使用线程池执行（避免阻塞事件循环）
        import asyncio

        loop = asyncio.get_event_loop()

        def embed_texts():
            return rag_service.embeddings.embed_documents(test_texts)

        embeddings = await loop.run_in_executor(None, embed_texts)

        print(f"生成了 {len(embeddings)} 个嵌入向量")
        print(f"每个向量的维度: {len(embeddings[0])}")

        # 计算相似度
        print("\n计算文本相似度:")

        # 比较"水稻稻瘟病"和其他文本的相似度
        query_embedding = embeddings[0]  # "水稻稻瘟病的症状是什么？"

        for i, text in enumerate(test_texts):
            if i == 0:
                continue

            # 计算余弦相似度
            similarity = np.dot(query_embedding, embeddings[i]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embeddings[i])
            )

            print(
                f"  '{test_texts[0][:10]}...' 与 '{text[:10]}...' 的相似度: {similarity:.4f}"
            )

        # 检查向量数据库的检索
        print("\n测试向量数据库检索...")

        if rag_service.vector_store:
            # 测试相似度检索
            retriever = rag_service.vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 3, "score_threshold": 0.5}
            )

            test_queries = ["稻瘟病症状", "种植密度", "灌溉方法"]

            for query in test_queries:
                print(f"\n查询: {query}")
                docs = await retriever.ainvoke(query)

                if docs:
                    print(f"检索到 {len(docs)} 个文档")

                    for j, doc in enumerate(docs):
                        content = doc.page_content
                        # 提取前几行作为标识
                        lines = content.splitlines()
                        identifier = ""
                        for line in lines[:3]:
                            if line.strip():
                                identifier = line[:50]
                                break

                        print(f"  文档 {j + 1}: {identifier}...")
                else:
                    print("未检索到文档")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_different_embedding_models():
    """测试不同的嵌入模型"""
    print("\n测试不同的嵌入模型...")

    try:
        # 尝试使用在线模型
        from langchain_huggingface import HuggingFaceEmbeddings

        models_to_test = [
            "sentence-transformers/all-MiniLM-L6-v2",  # 小模型
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 多语言
            "BAAI/bge-small-zh-v1.5",  # 中文优化
        ]

        for model_name in models_to_test:
            print(f"\n测试模型: {model_name}")

            try:
                # 创建嵌入模型
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )

                # 测试嵌入
                test_text = "水稻病害防治"
                embedding = embeddings.embed_query(test_text)

                print(f"  向量维度: {len(embedding)}")
                print(f"  模型可用")

            except Exception as e:
                print(f"  模型不可用: {e}")

        return True

    except Exception as e:
        print(f"模型测试失败: {e}")
        return False


async def fix_embedding_model():
    """修复嵌入模型"""
    print("\n修复嵌入模型配置...")

    try:
        # 更新配置使用更好的模型
        from config import settings

        # 建议使用中文优化的模型
        recommended_model = "BAAI/bge-small-zh-v1.5"

        print(f"当前嵌入模型: {settings.EMBEDDING_MODEL}")
        print(f"推荐嵌入模型: {recommended_model}")

        # 检查是否可以加载推荐模型
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            print("尝试加载推荐模型...")
            embeddings = HuggingFaceEmbeddings(
                model_name=recommended_model,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            # 测试嵌入
            test_text = "测试文本"
            embedding = embeddings.embed_query(test_text)
            print(f"推荐模型加载成功，向量维度: {len(embedding)}")

            return recommended_model

        except Exception as e:
            print(f"推荐模型加载失败: {e}")
            print("回退到默认模型")
            return settings.EMBEDDING_MODEL

    except Exception as e:
        print(f"修复失败: {e}")
        return None


async def rebuild_with_better_embedding():
    """使用更好的嵌入模型重建向量数据库"""
    print("\n使用更好的嵌入模型重建向量数据库...")

    try:
        import shutil

        # 1. 删除旧的向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            shutil.rmtree(vector_store_path)
            print("已删除旧的向量数据库")

        # 2. 使用更好的嵌入模型
        from yoloapp.rag import RAGService
        from langchain_huggingface import HuggingFaceEmbeddings

        # 尝试使用中文优化模型
        model_name = "BAAI/bge-small-zh-v1.5"

        print(f"使用嵌入模型: {model_name}")

        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            # 3. 创建新的RAG服务
            rag_service = RAGService(embeddings=embeddings)
            await rag_service.initialize()

            if rag_service.vector_store:
                print("向量数据库重建成功")

                # 4. 测试检索
                print("\n测试重建后的检索...")
                retriever = rag_service.vector_store.as_retriever(
                    search_kwargs={"k": 2}
                )

                test_queries = ["稻瘟病", "种植密度", "灌溉"]

                for query in test_queries:
                    docs = await retriever.ainvoke(query)
                    print(f"查询: {query} - 检索到 {len(docs)} 个文档")

                    if docs:
                        content_preview = docs[0].page_content[:80].replace("\n", " ")
                        print(f"  内容: {content_preview}...")

                return True
            else:
                print("向量数据库重建失败")
                return False

        except Exception as e:
            print(f"使用推荐模型失败: {e}")
            print("回退到默认配置...")

            # 使用默认配置
            from yoloapp.rag import get_rag_service

            global _rag_service_instance
            _rag_service_instance = None

            rag_service = get_rag_service()
            await rag_service.initialize()

            return rag_service.vector_store is not None

    except Exception as e:
        print(f"重建失败: {e}")
        return False


async def main():
    """主函数"""
    print("嵌入模型测试与修复")
    print("=" * 60)

    # 测试当前嵌入模型
    current_ok = await test_embeddings()

    if not current_ok:
        print("\n当前嵌入模型有问题，尝试修复...")

        # 测试其他模型
        await test_different_embedding_models()

        # 修复配置
        better_model = await fix_embedding_model()

        if better_model:
            print(f"\n建议使用模型: {better_model}")

            # 使用更好的模型重建
            rebuild_ok = await rebuild_with_better_embedding()

            if rebuild_ok:
                print("\n向量数据库重建成功！")

                # 重新测试
                print("\n重新测试嵌入模型...")
                await test_embeddings()
            else:
                print("\n向量数据库重建失败")
        else:
            print("\n无法找到合适的嵌入模型")

    print("\n" + "=" * 60)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())
