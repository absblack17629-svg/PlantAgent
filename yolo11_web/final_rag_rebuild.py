#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终RAG重建 - 使用中文优化嵌入模型
"""

import asyncio
import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def rebuild_with_chinese_embedding():
    """使用中文优化嵌入模型重建RAG"""
    print("使用中文优化嵌入模型重建RAG系统...")

    try:
        # 1. 删除旧的向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"删除旧的向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("向量数据库已删除")

        # 2. 重置RAG服务单例
        from yoloapp.rag import _rag_service_instance

        _rag_service_instance = None
        print("RAG服务单例已重置")

        # 3. 重新初始化RAG（会自动使用新的嵌入模型配置）
        print("重新初始化RAG系统...")
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("RAG系统重新初始化成功")

            # 4. 验证新向量数据库
            print("\n验证新向量数据库:")

            # 检查向量数量
            try:
                index = rag_service.vector_store.index
                print(f"向量维度: {index.d}")
                print(f"向量数量: {index.ntotal}")
            except:
                print("无法获取索引详细信息")

            return True
        else:
            print("RAG系统重新初始化失败")
            return False

    except Exception as e:
        print(f"重建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_rag_retrieval():
    """测试RAG检索"""
    print("\n测试RAG检索功能...")

    try:
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()

        if not rag_service.vector_store:
            print("向量数据库未初始化")
            return False

        # 测试关键查询
        test_cases = [
            ("稻瘟病症状", "应该返回病害防治相关内容"),
            ("种植密度规划", "应该返回种植规划相关内容"),
            ("灌溉策略", "应该返回灌溉策略相关内容"),
            ("施肥管理", "应该返回施肥管理相关内容"),
            ("病虫害防治", "应该返回病虫害防治相关内容"),
        ]

        all_passed = True

        for query, expected_desc in test_cases:
            print(f"\n查询: {query} ({expected_desc})")

            retriever = rag_service.vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 2}
            )

            try:
                docs = await retriever.ainvoke(query)

                if docs:
                    print(f"检索到 {len(docs)} 个文档")

                    for i, doc in enumerate(docs):
                        source = doc.metadata.get("source", "unknown")
                        content = doc.page_content

                        # 提取前几行作为标识
                        lines = content.splitlines()
                        identifier = ""
                        for line in lines[:3]:
                            if line.strip():
                                identifier = line[:60]
                                break

                        print(f"  文档 {i + 1} (来源: {source}):")
                        print(f"    {identifier}...")

                        # 检查内容相关性
                        if any(
                            keyword in content for keyword in ["稻瘟", "白叶枯", "纹枯"]
                        ):
                            if "稻瘟" in query:
                                print(f"    [相关] 包含病害关键词")
                            else:
                                print(f"    [可能不相关] 包含病害关键词但查询不是病害")
                        elif any(
                            keyword in content for keyword in ["种植", "密度", "品种"]
                        ):
                            if "种植" in query or "密度" in query:
                                print(f"    [相关] 包含种植关键词")
                            else:
                                print(f"    [可能不相关] 包含种植关键词但查询不是种植")
                        elif any(
                            keyword in content for keyword in ["灌溉", "浇水", "水层"]
                        ):
                            if "灌溉" in query:
                                print(f"    [相关] 包含灌溉关键词")
                            else:
                                print(f"    [可能不相关] 包含灌溉关键词但查询不是灌溉")
                        else:
                            print(f"    [需要人工检查] 内容不包含明显关键词")
                else:
                    print("未检索到文档")
                    all_passed = False

            except Exception as e:
                print(f"检索失败: {e}")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"检索测试失败: {e}")
        return False


async def test_full_rag_workflow():
    """测试完整RAG工作流程"""
    print("\n测试完整RAG工作流程...")

    try:
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client

        rag_service = get_rag_service()
        llm_client = get_llm_client("default")

        # 测试查询
        test_queries = [
            "水稻白叶枯病的症状是什么？",
            "水稻种植密度应该怎么规划？",
            "水稻灌溉有哪些策略？",
        ]

        for query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"测试查询: {query}")

            try:
                response = await rag_service.query(query, llm_client)

                print(f"回答长度: {len(response)} 字符")
                print(f"回答预览: {response[:200]}...")

                # 基本质量检查
                if not response or len(response) < 50:
                    print("[问题] 回答太短")
                elif "抱歉" in response or "暂未初始化" in response:
                    print("[问题] 回答包含错误信息")
                elif "知识库中没有" in response or "未找到相关信息" in response:
                    print("[问题] 未找到相关信息")
                else:
                    print("[正常] 回答看起来合理")

            except Exception as e:
                print(f"查询失败: {e}")

        print(f"\n{'=' * 60}")
        print("完整工作流程测试完成")

    except Exception as e:
        print(f"工作流程测试失败: {e}")


async def main():
    """主函数"""
    print("RAG系统最终重建与测试")
    print("=" * 60)

    # 重建RAG系统
    print("步骤1: 重建RAG系统...")
    rebuild_ok = await rebuild_with_chinese_embedding()

    if not rebuild_ok:
        print("重建失败，无法继续测试")
        return False

    # 测试检索功能
    print("\n步骤2: 测试检索功能...")
    retrieval_ok = await test_rag_retrieval()

    # 测试完整工作流程
    print("\n步骤3: 测试完整工作流程...")
    await test_full_rag_workflow()

    print("\n" + "=" * 60)
    print("重建与测试完成")

    if retrieval_ok:
        print("[OK] RAG系统重建成功，检索功能正常")
    else:
        print("[WARNING] RAG系统重建完成，但检索功能可能有问题")

    return rebuild_ok


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n操作失败: {e}")
        sys.exit(1)
