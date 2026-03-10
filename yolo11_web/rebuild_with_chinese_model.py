#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用本地中文模型重建向量数据库
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def load_chinese_embeddings():
    """加载中文优化嵌入模型"""
    print("加载中文优化嵌入模型: BAAI/bge-small-zh-v1.5")
    print("=" * 60)

    try:
        # 检查模型文件
        model_dir = "bge-small-zh-v1.5"
        if not os.path.exists(model_dir):
            print(f"错误: 模型目录不存在: {model_dir}")
            return None

        print(f"模型目录: {os.path.abspath(model_dir)}")

        # 检查必要文件
        required_files = ["config.json", "pytorch_model.bin", "vocab.txt"]
        for file in required_files:
            file_path = os.path.join(model_dir, file)
            if not os.path.exists(file_path):
                print(f"警告: 缺少文件 {file}")
            else:
                print(f"找到文件: {file}")

        # 导入必要的库
        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            print("使用 langchain_huggingface.HuggingFaceEmbeddings")
        except ImportError:
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings

                print("使用 langchain_community.embeddings.HuggingFaceEmbeddings")
            except ImportError:
                print("错误: 无法导入 HuggingFaceEmbeddings")
                return None

        # 创建嵌入模型（使用本地路径）
        print("\n创建嵌入模型...")
        embeddings = HuggingFaceEmbeddings(
            model_name=model_dir,  # 使用本地路径
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True, "batch_size": 32},
        )

        # 测试模型
        print("测试模型...")
        test_text = "这是一个测试句子"
        embedding = embeddings.embed_query(test_text)

        print(f"模型测试成功！")
        print(f"向量维度: {len(embedding)}")

        # 测试中文语义理解
        print("\n测试中文语义理解...")
        test_pairs = [
            ("水稻稻瘟病", "水稻病害"),
            ("种植密度", "农业规划"),
            ("灌溉策略", "水资源管理"),
        ]

        import numpy as np

        for text1, text2 in test_pairs:
            emb1 = embeddings.embed_query(text1)
            emb2 = embeddings.embed_query(text2)

            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )

            print(f"  '{text1}' 与 '{text2}' 相似度: {similarity:.4f}")

        return embeddings

    except Exception as e:
        print(f"加载模型失败: {e}")
        import traceback

        traceback.print_exc()
        return None


def rebuild_vector_store(embeddings):
    """使用中文模型重建向量数据库"""
    print("\n" + "=" * 60)
    print("重建向量数据库")
    print("=" * 60)

    try:
        # 1. 删除旧的向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            print(f"删除旧的向量数据库: {vector_store_path}")
            shutil.rmtree(vector_store_path)
            print("向量数据库已删除")

        # 2. 加载优化后的知识文档
        print("加载优化后的知识文档...")
        knowledge_file = "optimized_rice_knowledge.txt"
        if not os.path.exists(knowledge_file):
            print(f"错误: 知识文件不存在: {knowledge_file}")
            return False

        with open(knowledge_file, "r", encoding="utf-8") as f:
            knowledge_doc = f.read()

        print(f"知识文档大小: {len(knowledge_doc)} 字符")

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

        # 分割文档（针对中文优化）
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,  # 较小的chunk_size适合中文
            chunk_overlap=40,
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", "、", " ", ""],
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"文档分割成 {len(split_docs)} 个片段")

        # 显示一些片段
        print("\n文档片段示例:")
        for i, doc in enumerate(split_docs[:3]):
            content = doc.page_content
            print(f"  片段 {i + 1}: {content[:100]}...")

        # 创建向量数据库
        print("\n创建向量数据库（这可能需要几分钟）...")
        vector_store = FAISS.from_documents(split_docs, embeddings)

        # 保存
        vector_store.save_local(vector_store_path)
        print(f"向量数据库已保存到: {vector_store_path}")

        # 4. 测试检索
        print("\n测试新向量数据库检索...")
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

        test_queries = [
            "水稻稻瘟病怎么防治",
            "水稻种植密度多少合适",
            "水稻灌溉需要注意什么",
            "水稻施肥用什么肥料",
            "水稻收获后怎么储存",
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            docs = retriever.invoke(query)

            if docs:
                print(f"检索到 {len(docs)} 个文档")

                for i, doc in enumerate(docs):
                    content = doc.page_content
                    source = doc.metadata.get("source", "unknown")

                    # 提取标题或前几行
                    lines = content.splitlines()
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
                    print(f"    内容片段: {content[:100]}...")
            else:
                print("未检索到文档")

        return True

    except Exception as e:
        print(f"重建失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def update_configuration():
    """更新系统配置使用中文模型"""
    print("\n" + "=" * 60)
    print("更新系统配置")
    print("=" * 60)

    try:
        # 1. 更新settings.py
        settings_file = "config/settings.py"
        if not os.path.exists(settings_file):
            print(f"错误: 配置文件不存在: {settings_file}")
            return False

        with open(settings_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 确保使用正确的嵌入模型路径
        model_path = "bge-small-zh-v1.5"

        # 找到并替换嵌入模型配置
        import re

        # 替换EMBEDDING_MODEL配置
        new_content = re.sub(
            r'EMBEDDING_MODEL: str = ".*?"',
            f'EMBEDDING_MODEL: str = "{model_path}"',
            content,
        )

        with open(settings_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"已更新 {settings_file}")

        # 2. 更新config/__init__.py
        config_init_file = "config/__init__.py"
        if os.path.exists(config_init_file):
            with open(config_init_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 替换embedding_model配置
            new_content = re.sub(
                r'"embedding_model": ".*?"',
                f'"embedding_model": "{model_path}"',
                content,
            )

            with open(config_init_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"已更新 {config_init_file}")

        # 3. 更新yoloapp/rag.py中的嵌入模型配置
        rag_file = "yoloapp/rag.py"
        if os.path.exists(rag_file):
            with open(rag_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否有嵌入模型配置
            if "HuggingFaceEmbeddings" in content:
                # 查找并替换模型名称
                new_content = re.sub(
                    r'model_name=["\'].*?["\']',
                    f'model_name="{model_path}"',
                    content,
                )

                with open(rag_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"已更新 {rag_file}")

        print("\n配置更新完成！")
        return True

    except Exception as e:
        print(f"配置更新失败: {e}")
        return False


def main():
    """主函数"""
    print("使用中文优化模型重建RAG系统")
    print("=" * 60)

    # 1. 加载中文模型
    embeddings = load_chinese_embeddings()

    if not embeddings:
        print("\n模型加载失败，无法继续")
        return False

    # 2. 重建向量数据库
    rebuild_ok = rebuild_vector_store(embeddings)

    if not rebuild_ok:
        print("\n向量数据库重建失败")
        return False

    # 3. 更新配置
    config_ok = update_configuration()

    if not config_ok:
        print("\n配置更新失败")
        return False

    print("\n" + "=" * 60)
    print("[OK] 中文优化模型部署完成！")
    print("\n系统改进:")
    print("  1. [OK] 加载了中文优化嵌入模型 BAAI/bge-small-zh-v1.5")
    print("  2. [OK] 测试了中文语义理解能力")
    print("  3. [OK] 使用新模型重建了向量数据库")
    print("  4. [OK] 更新了系统配置")

    print("\n预期效果:")
    print("  - RAG检索相关性显著提升")
    print("  - 农业相关查询能返回更准确的结果")
    print("  - 系统整体性能改善")

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
