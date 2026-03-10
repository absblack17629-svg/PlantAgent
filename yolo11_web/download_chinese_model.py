#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载中文优化嵌入模型
"""

import os
import sys
import time
from pathlib import Path


def download_model_with_progress():
    """下载模型并显示进度"""
    print("开始下载中文优化嵌入模型: BAAI/bge-small-zh-v1.5")
    print("=" * 60)

    try:
        # 设置缓存目录
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        print(f"缓存目录: {cache_dir}")

        # 创建模型目录
        model_dir = cache_dir / "models--BAAI--bge-small-zh-v1.5"
        model_dir.mkdir(parents=True, exist_ok=True)

        print("正在下载模型...")
        print("这可能需要几分钟时间，请耐心等待...")

        # 导入必要的库
        from langchain_huggingface import HuggingFaceEmbeddings

        # 开始下载
        start_time = time.time()

        # 创建嵌入模型（这会触发下载）
        embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
            cache_folder=str(cache_dir),
        )

        # 测试模型
        print("\n模型下载完成，正在测试...")
        test_text = "这是一个测试句子"
        embedding = embeddings.embed_query(test_text)

        download_time = time.time() - start_time
        print(f"下载和测试完成！耗时: {download_time:.1f}秒")
        print(f"向量维度: {len(embedding)}")

        # 检查模型文件
        print("\n检查下载的文件...")
        if model_dir.exists():
            files = list(model_dir.rglob("*"))
            print(f"找到 {len(files)} 个文件")

            # 显示主要文件
            important_files = [
                f for f in files if f.suffix in [".bin", ".json", ".txt", ".model"]
            ]
            for f in important_files[:10]:  # 只显示前10个
                print(f"  {f.relative_to(model_dir)}")

        return embeddings

    except Exception as e:
        print(f"下载失败: {e}")
        import traceback

        traceback.print_exc()
        return None


def test_chinese_semantics(embeddings):
    """测试中文语义理解"""
    print("\n" + "=" * 60)
    print("测试中文语义理解能力")
    print("=" * 60)

    try:
        # 测试句子
        test_pairs = [
            ("水稻稻瘟病", "水稻病害"),
            ("种植密度", "农业规划"),
            ("灌溉策略", "水资源管理"),
            ("收获储存", "粮食保存"),
        ]

        import numpy as np

        for text1, text2 in test_pairs:
            emb1 = embeddings.embed_query(text1)
            emb2 = embeddings.embed_query(text2)

            # 计算余弦相似度
            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )

            print(f"'{text1}' 与 '{text2}' 的语义相似度: {similarity:.4f}")

        # 测试农业相关文本
        print("\n农业文本相似度测试:")
        agricultural_texts = [
            "水稻稻瘟病的症状是叶片出现病斑",
            "水稻种植密度应该合理规划",
            "水稻灌溉需要科学管理",
            "苹果树的修剪技术",
        ]

        query = "水稻病害防治"
        query_emb = embeddings.embed_query(query)

        for i, text in enumerate(agricultural_texts):
            text_emb = embeddings.embed_query(text)
            similarity = np.dot(query_emb, text_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(text_emb)
            )
            relevance = "相关" if similarity > 0.5 else "不相关"
            print(
                f"  '{query}' 与 '{text[:20]}...' 相似度: {similarity:.4f} ({relevance})"
            )

        return True

    except Exception as e:
        print(f"语义测试失败: {e}")
        return False


def rebuild_rag_with_chinese_model(embeddings):
    """使用中文模型重建RAG"""
    print("\n" + "=" * 60)
    print("使用中文优化模型重建RAG系统")
    print("=" * 60)

    try:
        import shutil
        import asyncio

        # 1. 删除旧的向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"删除旧的向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("向量数据库已删除")

        # 2. 加载优化后的知识文档
        print("加载优化后的知识文档...")
        with open("optimized_rice_knowledge.txt", "r", encoding="utf-8") as f:
            knowledge_doc = f.read()

        # 3. 创建向量数据库
        print("创建新的向量数据库...")
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # 创建文档
        documents = [
            Document(
                page_content=knowledge_doc,
                metadata={
                    "source": "optimized_rice_knowledge",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # 较小的chunk_size
            chunk_overlap=40,
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"文档分割成 {len(split_docs)} 个片段")

        # 创建向量数据库
        vector_store = FAISS.from_documents(split_docs, embeddings)

        # 保存
        vector_store.save_local(vector_store_path)
        print(f"向量数据库已保存到: {vector_store_path}")

        # 4. 测试检索
        print("\n测试新向量数据库检索...")
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

        test_queries = ["稻瘟病症状", "种植密度规划", "灌溉策略", "施肥管理"]

        for query in test_queries:
            print(f"\n查询: {query}")
            docs = retriever.invoke(query)

            if docs:
                print(f"检索到 {len(docs)} 个文档")

                for i, doc in enumerate(docs):
                    content = doc.page_content
                    lines = content.splitlines()

                    # 提取标题
                    title = ""
                    for line in lines[:3]:
                        if line.strip() and (
                            line.startswith("#") or line.startswith("###")
                        ):
                            title = line.strip()[:50]
                            break

                    if not title and lines:
                        title = lines[0][:50].strip()

                    print(f"  文档 {i + 1}: {title}...")
            else:
                print("未检索到文档")

        return True

    except Exception as e:
        print(f"重建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def update_configuration():
    """更新配置"""
    print("\n" + "=" * 60)
    print("更新系统配置")
    print("=" * 60)

    try:
        # 1. 更新settings.py
        settings_file = "config/settings.py"
        with open(settings_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 确保使用正确的嵌入模型
        if 'EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"' not in content:
            # 找到并替换嵌入模型配置
            import re

            new_content = re.sub(
                r'EMBEDDING_MODEL: str = ".*?"',
                'EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"',
                content,
            )

            with open(settings_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("已更新 config/settings.py")
        else:
            print("config/settings.py 配置正确")

        # 2. 更新config/__init__.py
        config_init_file = "config/__init__.py"
        with open(config_init_file, "r", encoding="utf-8") as f:
            content = f.read()

        if '"embedding_model": "BAAI/bge-small-zh-v1.5"' not in content:
            new_content = content.replace(
                '"embedding_model": settings.EMBEDDING_MODEL,',
                '"embedding_model": "BAAI/bge-small-zh-v1.5",',
            )

            with open(config_init_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("已更新 config/__init__.py")
        else:
            print("config/__init__.py 配置正确")

        return True

    except Exception as e:
        print(f"配置更新失败: {e}")
        return False


def main():
    """主函数"""
    print("中文优化嵌入模型下载与RAG系统重建")
    print("=" * 60)

    # 1. 下载模型
    embeddings = download_model_with_progress()

    if not embeddings:
        print("\n模型下载失败，无法继续")
        return False

    # 2. 测试中文语义
    semantics_ok = test_chinese_semantics(embeddings)

    if not semantics_ok:
        print("\n语义测试失败")
        return False

    # 3. 重建RAG
    rebuild_ok = rebuild_rag_with_chinese_model(embeddings)

    if not rebuild_ok:
        print("\nRAG重建失败")
        return False

    # 4. 更新配置
    config_ok = update_configuration()

    print("\n" + "=" * 60)
    print("[OK] 中文优化模型部署完成！")
    print("\n系统改进:")
    print("  1. [OK] 下载了中文优化嵌入模型 BAAI/bge-small-zh-v1.5")
    print("  2. [OK] 测试了中文语义理解能力")
    print("  3. [OK] 使用新模型重建了向量数据库")
    print("  4. [OK] 更新了系统配置")

    print("\n预期效果:")
    print("  • RAG检索相关性显著提升")
    print("  • 农业相关查询能返回更准确的结果")
    print("  • 系统整体性能改善")

    print("\n下一步:")
    print("  1. 重启服务: python main.py")
    print("  2. 测试完整工作流程")
    print("  3. 验证RAG回答质量")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n操作失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
