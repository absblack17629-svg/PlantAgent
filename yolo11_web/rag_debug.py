#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG调试脚本 - 不使用Unicode字符
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def debug_rag():
    """调试RAG系统"""
    print("=== RAG系统调试 ===")

    try:
        # 1. 检查知识文档
        print("\n1. 检查知识文档...")
        from yoloapp.rag import get_rice_disease_document

        doc = get_rice_disease_document()
        print(f"文档长度: {len(doc)} 字符")

        # 检查关键内容
        sections_to_check = [
            ("病害防治篇", "病害防治"),
            ("种植规划篇", "种植规划"),
            ("灌溉策略篇", "灌溉策略"),
        ]

        for section_name, keyword in sections_to_check:
            if section_name in doc:
                print(f"[OK] 包含: {section_name}")
            else:
                print(f"[ERROR] 缺少: {section_name}")

        # 2. 检查向量数据库
        print("\n2. 检查向量数据库...")
        vector_store_path = "./vector_store"

        if os.path.exists(vector_store_path):
            print(f"向量数据库目录存在: {vector_store_path}")
            files = os.listdir(vector_store_path)
            print(f"目录内容: {files}")
        else:
            print(f"向量数据库目录不存在")

        # 3. 初始化RAG服务
        print("\n3. 初始化RAG服务...")
        from yoloapp.rag import get_rag_service

        rag_service = get_rag_service()
        await rag_service.initialize()

        if rag_service.vector_store:
            print("RAG服务初始化成功")

            # 测试检索
            print("\n4. 测试知识检索...")
            retriever = rag_service.vector_store.as_retriever(search_kwargs={"k": 1})

            test_queries = ["水稻病害", "种植密度", "灌溉方法"]

            for query in test_queries:
                try:
                    docs = await retriever.ainvoke(query)
                    if docs:
                        doc = docs[0]
                        source = doc.metadata.get("source", "unknown")
                        content_preview = doc.page_content[:80].replace("\n", " ")
                        print(f"查询: {query}")
                        print(f"  来源: {source}")
                        print(f"  内容: {content_preview}...")
                    else:
                        print(f"查询: {query} - 未找到相关内容")
                except Exception as e:
                    print(f"查询 '{query}' 失败: {e}")
        else:
            print("RAG服务初始化失败，向量数据库为空")

            # 尝试重建
            print("\n5. 尝试重建向量数据库...")
            try:
                import shutil

                # 删除旧的
                if os.path.exists(vector_store_path):
                    shutil.rmtree(vector_store_path)
                    print("已删除旧的向量数据库")

                # 重置服务
                from yoloapp.rag import _rag_service_instance

                _rag_service_instance = None

                # 重新初始化
                rag_service = get_rag_service()
                await rag_service.initialize()

                if rag_service.vector_store:
                    print("向量数据库重建成功")
                else:
                    print("向量数据库重建失败")

            except Exception as e:
                print(f"重建失败: {e}")

        # 6. 检查LLM配置
        print("\n6. 检查LLM配置...")
        try:
            from config import settings

            print(f"模型: {settings.ZHIPU_MODEL}")
            print(f"API地址: {settings.ZHIPU_BASE_URL}")
            print(f"API密钥: {'已设置' if settings.ZHIPU_API_KEY else '未设置'}")

            # 检查是否为DeepSeek
            if "deepseek" in settings.ZHIPU_MODEL.lower():
                print("配置正确: 使用DeepSeek模型")
            else:
                print(f"警告: 模型不是DeepSeek: {settings.ZHIPU_MODEL}")

        except Exception as e:
            print(f"配置检查失败: {e}")

        print("\n=== 调试完成 ===")

    except Exception as e:
        print(f"调试过程中出现异常: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_rag())
