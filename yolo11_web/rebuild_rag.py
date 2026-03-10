#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重建RAG向量数据库
"""

import asyncio
import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def rebuild_rag():
    """重建RAG向量数据库"""
    print("开始重建RAG向量数据库...")

    try:
        vector_store_path = "./vector_store"

        # 1. 删除旧的向量数据库
        if os.path.exists(vector_store_path):
            print(f"删除旧的向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("向量数据库已删除")
        else:
            print("向量数据库目录不存在，无需删除")

        # 2. 重置RAG服务单例
        from yoloapp.rag import _rag_service_instance

        _rag_service_instance = None
        print("RAG服务单例已重置")

        # 3. 重新初始化RAG
        print("重新初始化RAG服务...")
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("RAG服务重新初始化成功")

            # 4. 验证新向量数据库
            print("\n验证新向量数据库...")

            # 检查向量数量
            try:
                index = rag_service.vector_store.index
                print(f"向量维度: {index.d}")
                print(f"向量数量: {index.ntotal}")

                # 测试检索
                test_queries = ["稻瘟病症状", "种植密度", "灌溉策略"]

                for query in test_queries:
                    retriever = rag_service.vector_store.as_retriever(
                        search_kwargs={"k": 1}
                    )
                    docs = await retriever.ainvoke(query)

                    if docs:
                        doc = docs[0]
                        source = doc.metadata.get("source", "unknown")
                        content_preview = doc.page_content[:100].replace("\n", " ")
                        print(f"\n查询: {query}")
                        print(f"  来源: {source}")
                        print(f"  内容: {content_preview}...")
                    else:
                        print(f"\n查询: {query} - 未找到相关文档")

            except Exception as e:
                print(f"验证失败: {e}")

            return True
        else:
            print("RAG服务重新初始化失败")
            return False

    except Exception as e:
        print(f"重建过程失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def verify_rag_content():
    """验证RAG内容"""
    print("\n验证RAG内容...")

    try:
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()

        # 确保已初始化
        await rag_service.initialize()

        if not rag_service.vector_store:
            print("向量数据库未初始化")
            return False

        # 测试关键查询
        key_queries = {
            "病害防治": ["稻瘟病", "白叶枯病", "纹枯病"],
            "种植规划": ["种植密度", "品种选择", "生育期管理"],
            "灌溉策略": ["浅湿灌溉", "节水灌溉", "土壤类型"],
        }

        all_passed = True

        for category, queries in key_queries.items():
            print(f"\n{category}测试:")

            for query in queries:
                retriever = rag_service.vector_store.as_retriever(
                    search_kwargs={"k": 1}
                )
                docs = await retriever.ainvoke(query)

                if docs:
                    doc = docs[0]
                    content = doc.page_content

                    # 检查内容是否相关
                    if any(keyword in content for keyword in queries):
                        print(f"  ✓ {query}: 检索到相关文档")
                    else:
                        print(f"  ✗ {query}: 检索到不相关文档")
                        all_passed = False
                else:
                    print(f"  ✗ {query}: 未检索到文档")
                    all_passed = False

        return all_passed

    except Exception as e:
        print(f"验证失败: {e}")
        return False


async def main():
    """主函数"""
    print("=== RAG向量数据库重建 ===")

    # 重建向量数据库
    if await rebuild_rag():
        print("\n重建成功！")

        # 验证内容
        if await verify_rag_content():
            print("\n✓ RAG内容验证通过")
        else:
            print("\n✗ RAG内容验证失败")

        # 运行一个完整的RAG查询测试
        print("\n运行完整RAG查询测试...")
        await test_full_rag_query()
    else:
        print("\n重建失败！")

    print("\n=== 重建完成 ===")


async def test_full_rag_query():
    """测试完整的RAG查询"""
    try:
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client

        rag_service = get_rag_service()
        llm_client = get_llm_client("default")

        test_cases = [
            {
                "query": "水稻白叶枯病的症状是什么？",
                "expected_keywords": ["白叶枯病", "症状", "叶缘", "水渍状"],
            },
            {
                "query": "水稻种植密度应该怎么规划？",
                "expected_keywords": ["种植密度", "每亩", "万穴", "行距"],
            },
            {
                "query": "水稻灌溉有哪些策略？",
                "expected_keywords": ["灌溉", "浅湿", "节水", "水层"],
            },
        ]

        for test_case in test_cases:
            query = test_case["query"]
            expected_keywords = test_case["expected_keywords"]

            print(f"\n测试查询: {query}")

            try:
                response = await rag_service.query(query, llm_client)
                print(f"回答长度: {len(response)} 字符")
                print(f"回答预览: {response[:150]}...")

                # 检查是否包含预期关键词
                found_keywords = []
                for keyword in expected_keywords:
                    if keyword in response:
                        found_keywords.append(keyword)

                if found_keywords:
                    print(f"✓ 包含关键词: {found_keywords}")
                else:
                    print(f"✗ 未找到预期关键词")

            except Exception as e:
                print(f"查询失败: {e}")

    except Exception as e:
        print(f"完整测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
