#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析文档分割问题
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def analyze_document():
    """分析文档分割"""
    print("分析文档分割问题...")

    try:
        from yoloapp.rag import get_rice_disease_document
        from langchain_core.documents import Document
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # 获取文档
        doc_content = get_rice_disease_document()

        print(f"原始文档长度: {len(doc_content)} 字符")
        print(f"原始文档行数: {len(doc_content.splitlines())} 行")

        # 显示文档结构
        print("\n文档结构:")
        lines = doc_content.splitlines()
        for i, line in enumerate(lines[:50]):  # 只显示前50行
            if line.strip() and (
                line.startswith("#") or line.startswith("**") or "篇" in line
            ):
                print(f"行 {i + 1}: {line}")

        # 分析问题
        print("\n分析问题:")

        # 检查文档结尾
        print("文档结尾部分:")
        for i, line in enumerate(lines[-10:]):
            print(f"行 {len(lines) - 10 + i + 1}: {line}")

        # 检查文本分割
        print("\n使用当前分割器分割文档...")
        documents = [
            Document(
                page_content=doc_content,
                metadata={
                    "source": "rice_disease_manual",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        split_docs = text_splitter.split_documents(documents)

        print(f"分割成 {len(split_docs)} 个片段")

        # 分析每个片段的内容
        print("\n片段内容分析:")
        for i, doc in enumerate(split_docs):
            content = doc.page_content
            lines = content.splitlines()

            print(f"\n片段 {i + 1} (长度: {len(content)} 字符):")

            # 找片段的关键词
            keywords = []
            for line in lines[:5]:  # 检查前5行
                if line.strip():
                    # 提取可能的标题或关键词
                    if "#" in line or "**" in line or "：" in line or "。" in line:
                        keywords.append(line[:50].strip())

            if keywords:
                print(f"  关键词: {' | '.join(keywords[:3])}")

            # 检查内容分布
            sections = [
                "病害防治",
                "种植规划",
                "灌溉策略",
                "施肥管理",
                "病虫害综合",
                "收获储存",
            ]
            found_sections = []
            for section in sections:
                if section in content:
                    found_sections.append(section)

            if found_sections:
                print(f"  包含章节: {', '.join(found_sections)}")

            # 显示片段开头
            if lines:
                print(f"  开头: {lines[0][:80]}...")

        # 检查问题：是否所有片段都包含"收获与储存篇"？
        harvest_count = 0
        for doc in split_docs:
            if "收获与储存篇" in doc.page_content:
                harvest_count += 1

        print(f"\n问题分析:")
        print(f"  包含'收获与储存篇'的片段数: {harvest_count}/{len(split_docs)}")

        if harvest_count == len(split_docs):
            print("  [严重问题] 所有片段都包含'收获与储存篇'，这可能是因为文档结构问题")
        elif harvest_count > 0:
            print(f"  [问题] 有 {harvest_count} 个片段包含'收获与储存篇'")

        # 建议修复
        print("\n建议修复:")
        print("  1. 检查文档结尾是否被重复包含")
        print("  2. 调整分割参数（chunk_size, chunk_overlap）")
        print("  3. 确保文档结构清晰，使用明确的分隔符")

    except Exception as e:
        print(f"分析失败: {e}")
        import traceback

        traceback.print_exc()


def fix_document_structure():
    """修复文档结构"""
    print("\n修复文档结构...")

    try:
        from yoloapp.rag import get_rice_disease_document

        # 获取原始文档
        original_doc = get_rice_disease_document()

        # 检查文档结构
        lines = original_doc.splitlines()

        # 找到"收获与储存篇"的位置
        harvest_start = -1
        for i, line in enumerate(lines):
            if "收获与储存篇" in line:
                harvest_start = i
                break

        if harvest_start >= 0:
            print(f"找到'收获与储存篇'开始于行 {harvest_start + 1}")

            # 检查是否有重复内容
            harvest_content = "\n".join(lines[harvest_start:])

            # 检查"收获与储存篇"是否出现在文档开头附近
            early_occurrence = False
            for i in range(min(50, len(lines))):
                if "收获与储存篇" in lines[i]:
                    early_occurrence = True
                    print(f"  警告: '收获与储存篇'也出现在行 {i + 1}")
                    break

            if early_occurrence:
                print("  [问题] '收获与储存篇'可能被重复包含在文档中")

                # 创建修复后的文档
                # 只保留第一个"收获与储存篇"之前的内容
                fixed_lines = []
                harvest_found = False

                for line in lines:
                    if "收获与储存篇" in line:
                        if not harvest_found:
                            harvest_found = True
                            fixed_lines.append(line)
                        else:
                            # 跳过重复的部分
                            continue
                    else:
                        fixed_lines.append(line)

                fixed_doc = "\n".join(fixed_lines)

                print(
                    f"  修复后文档长度: {len(fixed_doc)} 字符 (原: {len(original_doc)} 字符)"
                )

                # 保存修复后的文档
                with open("fixed_document.txt", "w", encoding="utf-8") as f:
                    f.write(fixed_doc)

                print("  已保存修复后的文档到 fixed_document.txt")
                return fixed_doc

        print("  文档结构看起来正常")
        return original_doc

    except Exception as e:
        print(f"修复失败: {e}")
        return None


if __name__ == "__main__":
    analyze_document()
    fix_document_structure()
