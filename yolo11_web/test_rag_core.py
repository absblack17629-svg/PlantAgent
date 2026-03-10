#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心RAG测试 - 绕过日志问题
"""

import asyncio
import sys
import os

# 禁用日志
import loguru

loguru.logger.remove()

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def main():
    """主测试函数"""
    print("RAG知识库核心测试")
    print("=" * 60)

    try:
        # 1. 测试知识文档
        print("1. 测试知识文档内容...")
        from yoloapp.rag import get_rice_disease_document

        doc_content = get_rice_disease_document()
        print(f"  文档长度: {len(doc_content)} 字符")
        print(f"  文档行数: {len(doc_content.splitlines())} 行")

        # 检查关键章节
        key_sections = ["病害防治篇", "种植规划篇", "灌溉策略篇"]
        for section in key_sections:
            if section in doc_content:
                print(f"  ✓ 包含章节: {section}")
            else:
                print(f"  ✗ 缺少章节: {section}")

        # 2. 测试RAG初始化
        print("\n2. 初始化RAG服务...")
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("  ✓ 向量数据库已初始化")
        else:
            print("  ✗ 向量数据库初始化失败")

        # 3. 测试向量数据库检索
        print("\n3. 测试向量数据库检索...")
        if rag_service.vector_store:
            retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 2})

            test_questions = ["水稻白叶枯病", "水稻种植密度", "水稻灌溉"]

            for question in test_questions:
                docs = await retriever.ainvoke(question)
                print(f"  问题: {question}")
                print(f"    检索到 {len(docs)} 个文档")
                if docs:
                    source = docs[0].metadata.get("source", "unknown")
                    preview = docs[0].page_content[:100].replace("\n", " ")
                    print(f"    来源: {source}")
                    print(f"    预览: {preview}...")
        else:
            print("  ✗ 向量数据库不可用")

        # 4. 测试LLM配置
        print("\n4. 测试LLM配置...")
        try:
            from config import settings

            print(f"  模型: {settings.ZHIPU_MODEL}")
            print(f"  API地址: {settings.ZHIPU_BASE_URL}")
            print(f"  API密钥: {'已设置' if settings.ZHIPU_API_KEY else '未设置'}")
        except Exception as e:
            print(f"  ✗ LLM配置检查失败: {e}")

        # 5. 如果向量数据库有问题，重建
        print("\n5. 检查向量数据库状态...")
        vector_store_path = "./vector_store"

        if os.path.exists(vector_store_path):
            print(f"  ✓ 向量数据库目录存在: {vector_store_path}")
            files = os.listdir(vector_store_path)
            print(f"    包含文件: {files}")
        else:
            print(f"  ✗ 向量数据库目录不存在")

        # 6. 建议重建（如果需要）
        if not rag_service.vector_store:
            print("\n6. 重建向量数据库...")
            try:
                import shutil

                # 删除现有目录
                if os.path.exists(vector_store_path):
                    shutil.rmtree(vector_store_path)
                    print("  ✓ 已删除旧的向量数据库")

                # 重置RAG服务
                from yoloapp.rag import _rag_service_instance

                _rag_service_instance = None

                # 重新初始化
                rag_service = get_rag_service()
                await rag_service.initialize()

                if rag_service.vector_store:
                    print("  ✓ 向量数据库重建成功")
                else:
                    print("  ✗ 向量数据库重建失败")

            except Exception as e:
                print(f"  ✗ 重建失败: {e}")

        print("\n" + "=" * 60)
        print("测试完成")

    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
