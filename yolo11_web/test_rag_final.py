#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终RAG测试
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_rag_query():
    """测试RAG查询"""
    print("测试RAG查询功能...")

    try:
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client

        rag_service = get_rag_service()
        llm_client = get_llm_client("default")

        # 确保已初始化
        await rag_service.initialize()

        # 测试查询
        test_cases = [
            {"query": "水稻白叶枯病的症状是什么？", "description": "测试病害防治知识"},
            {"query": "水稻种植密度应该怎么规划？", "description": "测试种植规划知识"},
            {"query": "水稻灌溉有哪些策略？", "description": "测试灌溉策略知识"},
        ]

        all_passed = True

        for test_case in test_cases:
            query = test_case["query"]
            description = test_case["description"]

            print(f"\n{'=' * 60}")
            print(f"测试: {description}")
            print(f"查询: {query}")

            try:
                # 执行RAG查询
                response = await rag_service.query(query, llm_client)

                print(f"\n回答长度: {len(response)} 字符")
                print(f"回答预览: {response[:200]}...")

                # 检查回答质量
                if not response or len(response) < 50:
                    print("[FAIL] 回答太短")
                    all_passed = False
                elif "抱歉" in response or "暂未初始化" in response:
                    print("[FAIL] 回答包含错误信息")
                    all_passed = False
                else:
                    print("[PASS] 回答看起来正常")

            except Exception as e:
                print(f"[FAIL] 查询失败: {e}")
                all_passed = False

        print(f"\n{'=' * 60}")
        if all_passed:
            print("所有测试通过！")
        else:
            print("部分测试失败")

        return all_passed

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_rag_retrieval():
    """测试RAG检索（不调用LLM）"""
    print("\n测试RAG检索功能...")

    try:
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if not rag_service.vector_store:
            print("向量数据库未初始化")
            return False

        # 测试检索
        test_queries = [
            "稻瘟病症状",
            "种植密度规划",
            "灌溉方法",
            "施肥管理",
            "病虫害防治",
        ]

        print("检索测试结果:")

        for query in test_queries:
            retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 2})
            docs = await retriever.ainvoke(query)

            print(f"\n查询: {query}")
            print(f"检索到 {len(docs)} 个文档")

            for i, doc in enumerate(docs):
                source = doc.metadata.get("source", "unknown")
                content_preview = doc.page_content[:80].replace("\n", " ")
                print(f"  文档 {i + 1} (来源: {source}):")
                print(f"    {content_preview}...")

        return True

    except Exception as e:
        print(f"检索测试失败: {e}")
        return False


async def check_rag_configuration():
    """检查RAG配置"""
    print("\n检查RAG配置...")

    try:
        # 检查知识文档
        from yoloapp.rag import get_rice_disease_document

        doc = get_rice_disease_document()
        print(f"知识文档长度: {len(doc)} 字符")

        # 检查关键章节
        sections = [
            "病害防治篇",
            "种植规划篇",
            "灌溉策略篇",
            "施肥管理篇",
            "病虫害综合防治篇",
            "收获与储存篇",
        ]

        for section in sections:
            if section in doc:
                print(f"  [OK] {section}")
            else:
                print(f"  [MISSING] {section}")

        # 检查向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"\n向量数据库目录: {vector_store_path}")
            files = os.listdir(vector_store_path)
            print(f"文件: {files}")
        else:
            print(f"\n向量数据库目录不存在")
            return False

        return True

    except Exception as e:
        print(f"配置检查失败: {e}")
        return False


async def main():
    """主函数"""
    print("RAG系统最终测试")
    print("=" * 60)

    # 检查配置
    config_ok = await check_rag_configuration()

    if not config_ok:
        print("\n配置检查失败，无法继续测试")
        return False

    # 测试检索
    retrieval_ok = await test_rag_retrieval()

    # 测试完整查询
    query_ok = await test_rag_query()

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"  配置检查: {'通过' if config_ok else '失败'}")
    print(f"  检索测试: {'通过' if retrieval_ok else '失败'}")
    print(f"  查询测试: {'通过' if query_ok else '失败'}")

    overall = config_ok and retrieval_ok and query_ok
    print(f"\n总体结果: {'所有测试通过！' if overall else '部分测试失败'}")

    return overall


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试发生异常: {e}")
        sys.exit(1)
