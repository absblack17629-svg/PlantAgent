#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG知识库扩展验证
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.rag import get_rag_service, get_rice_disease_document
from yoloapp.llm import get_llm_client


async def test_rag_initialization():
    """测试RAG初始化"""
    print("[TEST] 测试RAG服务初始化...")

    try:
        # 获取RAG服务
        rag_service = get_rag_service()

        # 初始化RAG
        await rag_service.initialize()

        print("[OK] RAG服务初始化成功")
        return True
    except Exception as e:
        print(f"[ERROR] RAG服务初始化失败: {e}")
        return False


async def test_rag_query():
    """测试RAG查询功能"""
    print("\n[TEST] 测试RAG知识库查询...")

    try:
        # 获取服务和LLM
        rag_service = get_rag_service()
        llm_client = get_llm_client("default")

        # 确保已初始化
        await rag_service.initialize()

        # 测试查询
        test_queries = [
            "水稻白叶枯病的症状是什么？",
            "水稻种植密度应该怎么规划？",
            "水稻灌溉策略有哪些？",
            "水稻施肥管理有什么原则？",
            "如何防治稻飞虱？",
        ]

        for query in test_queries:
            print(f"\n[NOTE] 查询: {query}")
            try:
                response = await rag_service.query(query, llm_client)
                print(f"[TIP] 回答长度: {len(response)} 字符")
                print(
                    f"[DOC] 回答预览: {response[:200]}{'...' if len(response) > 200 else ''}"
                )

                # 检查回答是否包含我们新增的知识
                if "抱歉" in response or "暂未初始化" in response or len(response) < 50:
                    print(f"[WARNING] 回答可能有问题: 内容过短或包含错误提示")
                else:
                    print("[OK] 回答正常")

            except Exception as e:
                print(f"[ERROR] 查询失败: {e}")

        return True
    except Exception as e:
        print(f"[ERROR] RAG查询测试失败: {e}")
        return False


async def test_knowledge_content():
    """测试知识文档内容"""
    print("\n[TEST] 测试知识文档内容...")

    try:
        # 获取知识文档
        doc_content = get_rice_disease_document()

        print(f"[BOOK] 文档总长度: {len(doc_content)} 字符")
        print(f"📑 文档行数: {len(doc_content.splitlines())} 行")

        # 检查文档是否包含我们扩充的内容
        required_sections = [
            "病害防治篇",
            "种植规划篇",
            "灌溉策略篇",
            "施肥管理篇",
            "病虫害综合防治篇",
            "收获与储存篇",
        ]

        missing_sections = []
        for section in required_sections:
            if section in doc_content:
                print(f"[OK] 包含章节: {section}")
            else:
                missing_sections.append(section)
                print(f"[ERROR] 缺少章节: {section}")

        if missing_sections:
            print(f"[WARNING] 共缺少 {len(missing_sections)} 个章节")
            return False
        else:
            print("[OK] 所有章节都存在")
            return True

    except Exception as e:
        print(f"[ERROR] 测试知识文档失败: {e}")
        return False


async def test_vector_store_integrity():
    """测试向量数据库完整性"""
    print("\n[TEST] 测试向量数据库完整性...")

    try:
        from yoloapp.rag import get_rag_service
        from config import RAG_CONFIG

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store is None:
            print("[ERROR] 向量数据库未初始化")
            return False

        # 检查向量数据库是否有文档
        try:
            # 尝试检索测试查询
            retriever = rag_service.vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 3}
            )

            test_question = "水稻病害"
            docs = await retriever.ainvoke(test_question)

            print(f"[OK] 向量数据库正常，检索到 {len(docs)} 个文档")

            # 检查文档内容
            for i, doc in enumerate(docs[:2], 1):
                source = doc.metadata.get("source", "unknown")
                content_preview = doc.page_content[:100].replace("\n", " ")
                print(f"  文档 {i} (来源: {source}): {content_preview}...")

            return True

        except Exception as e:
            print(f"[ERROR] 向量数据库检索失败: {e}")
            return False

    except Exception as e:
        print(f"[ERROR] 向量数据库测试失败: {e}")
        return False


async def test_rebuild_vector_store():
    """测试重建向量数据库"""
    print("\n[TEST] 测试重建向量数据库...")

    try:
        import shutil
        import os

        vector_store_path = "./vector_store"

        if os.path.exists(vector_store_path):
            print(f"[DELETE] 删除现有向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("[OK] 向量数据库已删除")
        else:
            print("ℹ️ 向量数据库不存在，无需删除")

        # 重建RAG服务
        from yoloapp.rag import get_rag_service

        global _rag_service_instance
        _rag_service_instance = None

        rag_service = get_rag_service()

        # 重新初始化
        print("[REFRESH_CW] 重新初始化RAG服务...")
        await rag_service.initialize()

        print("[OK] 向量数据库重建完成")
        return True

    except Exception as e:
        print(f"[ERROR] 重建向量数据库失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("[START] 开始RAG知识库扩展验证测试")
    print("=" * 60)

    # 测试知识文档内容
    doc_test_passed = await test_knowledge_content()

    # 测试RAG初始化
    init_test_passed = await test_rag_initialization()

    # 测试向量数据库完整性
    vector_test_passed = await test_vector_store_integrity()

    # 测试RAG查询
    query_test_passed = await test_rag_query()

    print("\n" + "=" * 60)
    print("[CHART] 测试结果汇总:")
    print(f"  知识文档测试: {'[OK] 通过' if doc_test_passed else '[ERROR] 失败'}")
    print(f"  RAG初始化测试: {'[OK] 通过' if init_test_passed else '[ERROR] 失败'}")
    print(f"  向量数据库测试: {'[OK] 通过' if vector_test_passed else '[ERROR] 失败'}")
    print(f"  RAG查询测试: {'[OK] 通过' if query_test_passed else '[ERROR] 失败'}")

    # 如果测试失败，建议重建向量数据库
    if not (
        doc_test_passed
        and init_test_passed
        and vector_test_passed
        and query_test_passed
    ):
        print("\n[WARNING] 部分测试失败，建议重建向量数据库")
        rebuild = input("是否重建向量数据库？(y/n): ")
        if rebuild.lower() == "y":
            await test_rebuild_vector_store()
            # 重新测试
            print("\n[REFRESH_CW] 重新测试...")
            return await main()

    return all(
        [doc_test_passed, init_test_passed, vector_test_passed, query_test_passed]
    )


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[ERROR] 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 测试发生异常: {e}")
        sys.exit(1)
