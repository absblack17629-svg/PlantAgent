#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前RAG检索效果
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def test_rag_retrieval():
    """测试RAG检索"""
    print("测试当前RAG检索效果")
    print("=" * 60)

    try:
        # 导入必要的模块
        from yoloapp.rag import (
            get_rag_service,
            enhance_query_with_keywords,
            extract_keywords,
        )
        from yoloapp.llm import get_llm_client

        # 获取服务
        rag_service = get_rag_service()
        llm = get_llm_client("default")

        # 确保RAG服务已初始化
        if hasattr(rag_service, "init_async"):
            await rag_service.init_async()

        # 测试查询
        test_queries = [
            "水稻稻瘟病怎么防治",
            "水稻种植密度多少合适",
            "水稻灌溉需要注意什么",
            "水稻施肥用什么肥料",
            "水稻收获后怎么储存",
        ]

        for query in test_queries:
            print(f"\n查询: {query}")

            # 提取关键词
            keywords = extract_keywords(query)
            print(f"提取关键词: {keywords}")

            # 增强查询
            enhanced_query = enhance_query_with_keywords(query)
            print(f"增强查询: {enhanced_query}")

            # 调用RAG服务（如果可用）
            if hasattr(rag_service, "query_knowledge_base"):
                try:
                    result = await rag_service.query_knowledge_base(enhanced_query, llm)
                    print(f"RAG结果: {result[:200]}...")
                except Exception as e:
                    print(f"RAG查询失败: {e}")
                    print("尝试直接检索...")

                    # 尝试直接检索
                    if hasattr(rag_service, "vector_store"):
                        retriever = rag_service.vector_store.as_retriever(
                            search_type="similarity", search_kwargs={"k": 3}
                        )

                        # 直接检索
                        from langchain_core.documents import Document

                        if hasattr(retriever, "ainvoke"):
                            docs = await retriever.ainvoke(enhanced_query)
                        else:
                            docs = retriever.invoke(enhanced_query)

                        print(f"检索到 {len(docs)} 个文档")
                        for i, doc in enumerate(docs, 1):
                            content = doc.page_content
                            source = doc.metadata.get("source", "unknown")
                            print(f"  文档 {i} (来源: {source}):")
                            print(f"    内容: {content[:150]}...")
            else:
                print("RAG服务没有query_knowledge_base方法")
                print("检查rag_service对象:", type(rag_service))
                print("对象属性:", dir(rag_service)[:10])

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_rag_retrieval()

    if success:
        print("\n" + "=" * 60)
        print("[OK] 测试完成")
    else:
        print("\n" + "=" * 60)
        print("[FAIL] 测试失败")

    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
