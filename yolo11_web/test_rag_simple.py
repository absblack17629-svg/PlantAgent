#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试RAG知识库
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_knowledge_content():
    """测试知识文档内容"""
    print("测试RAG知识文档内容...")

    try:
        from yoloapp.rag import get_rice_disease_document

        # 获取知识文档
        doc_content = get_rice_disease_document()

        print(f"文档总长度: {len(doc_content)} 字符")
        print(f"文档行数: {len(doc_content.splitlines())} 行")

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
                print(f"包含章节: {section}")
            else:
                missing_sections.append(section)
                print(f"缺少章节: {section}")

        if missing_sections:
            print(f"共缺少 {len(missing_sections)} 个章节")
            return False
        else:
            print("所有章节都存在")
            return True

    except Exception as e:
        print(f"测试知识文档失败: {e}")
        return False


async def test_rag_query():
    """测试RAG查询功能"""
    print("\n测试RAG知识库查询...")

    try:
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client

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
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            try:
                response = await rag_service.query(query, llm_client)
                print(f"回答长度: {len(response)} 字符")
                print(
                    f"回答预览: {response[:200]}{'...' if len(response) > 200 else ''}"
                )

                # 检查回答是否包含我们新增的知识
                if "抱歉" in response or "暂未初始化" in response or len(response) < 50:
                    print(f"回答可能有问题: 内容过短或包含错误提示")
                else:
                    print("回答正常")

            except Exception as e:
                print(f"查询失败: {e}")

        return True
    except Exception as e:
        print(f"RAG查询测试失败: {e}")
        return False


async def test_vector_store():
    """测试向量数据库"""
    print("\n测试向量数据库...")

    try:
        from yoloapp.rag import get_rag_service
        import shutil

        # 检查向量数据库目录
        vector_store_path = "./vector_store"

        if os.path.exists(vector_store_path):
            print(f"向量数据库目录存在: {vector_store_path}")
            files = os.listdir(vector_store_path)
            print(f"目录中的文件: {files}")
        else:
            print(f"向量数据库目录不存在: {vector_store_path}")
            return False

        # 检查RAG服务
        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store is None:
            print("向量数据库未初始化")
            return False

        print("向量数据库已初始化")
        return True

    except Exception as e:
        print(f"向量数据库测试失败: {e}")
        return False


def check_llm_config():
    """检查LLM配置"""
    print("\n检查LLM配置...")

    try:
        from config import settings

        print(f"模型名称: {settings.ZHIPU_MODEL}")
        print(f"API地址: {settings.ZHIPU_BASE_URL}")
        print(f"API密钥: {'已设置' if settings.ZHIPU_API_KEY else '未设置'}")

        # 检查是否为DeepSeek模型
        if "deepseek" in settings.ZHIPU_MODEL.lower():
            print("使用的是DeepSeek模型")
            return True
        else:
            print(f"警告: 使用的模型不是DeepSeek: {settings.ZHIPU_MODEL}")
            return False

    except Exception as e:
        print(f"配置检查失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("开始RAG知识库测试")
    print("=" * 60)

    # 测试知识文档内容
    doc_test_passed = test_knowledge_content()

    # 检查LLM配置
    config_test_passed = check_llm_config()

    # 测试向量数据库
    vector_test_passed = await test_vector_store()

    # 测试RAG查询
    query_test_passed = await test_rag_query()

    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"  知识文档测试: {'通过' if doc_test_passed else '失败'}")
    print(f"  LLM配置测试: {'通过' if config_test_passed else '失败'}")
    print(f"  向量数据库测试: {'通过' if vector_test_passed else '失败'}")
    print(f"  RAG查询测试: {'通过' if query_test_passed else '失败'}")

    # 如果测试失败，建议重建向量数据库
    if not (doc_test_passed and vector_test_passed and query_test_passed):
        print("\n部分测试失败，建议重建向量数据库")
        answer = input("是否重建向量数据库？(y/n): ")
        if answer.lower() == "y":
            print("\n重建向量数据库...")
            try:
                import shutil

                vector_store_path = "./vector_store"

                if os.path.exists(vector_store_path):
                    shutil.rmtree(vector_store_path)
                    print("向量数据库已删除")

                # 重新初始化RAG
                from yoloapp.rag import get_rag_service

                global _rag_service_instance
                _rag_service_instance = None

                rag_service = get_rag_service()
                await rag_service.initialize()
                print("向量数据库重建完成")

                # 重新测试
                print("\n重新测试...")
                vector_test_passed = await test_vector_store()
                query_test_passed = await test_rag_query()

            except Exception as e:
                print(f"重建失败: {e}")

    return all(
        [doc_test_passed, config_test_passed, vector_test_passed, query_test_passed]
    )


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
