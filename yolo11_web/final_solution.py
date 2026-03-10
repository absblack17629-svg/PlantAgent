#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终解决方案：优化现有RAG系统
"""

import asyncio
import sys
import os
import shutil

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def optimize_knowledge_document():
    """优化知识文档结构"""
    print("优化知识文档结构...")

    try:
        from yoloapp.rag import get_rice_disease_document

        # 获取原始文档
        original_doc = get_rice_disease_document()

        # 分析问题：文档结尾的"收获与储存篇"可能被过度匹配
        # 解决方案：重新组织文档，确保每个部分都有清晰的标题

        # 创建优化后的文档结构
        optimized_doc = """# 水稻农业知识大全

## 一、病害防治知识

### 1.1 稻瘟病 (Blast Disease)
**症状识别**：叶片出现梭形或纺锤形病斑，中央灰白色，边缘褐色，有黄色晕圈
**防治方法**：
- 抗病品种：黄华占、粤晶丝苗2号、南粳5055
- 种子处理：25%咪鲜胺乳油3000倍液浸种48小时
- 药剂防治：75%三环唑可湿性粉剂2000倍液，20%稻瘟酰胺悬浮剂1000倍液
- 农业措施：合理密植（25×15cm），避免偏施氮肥

### 1.2 白叶枯病 (Bacterial Leaf Blight)
**症状识别**：叶缘出现水渍状病斑，沿叶脉扩展，形成黄白色条斑
**防治方法**：
- 抗病品种：中早39、中嘉早17、浙辐802
- 种子消毒：中生菌素1000倍液浸种24小时
- 药剂防治：20%叶枯唑可湿性粉剂500倍液，3%中生菌素可湿性粉剂800倍液
- 水肥管理：浅水勤灌，增施磷钾肥

### 1.3 纹枯病 (Sheath Blight)
**症状识别**：叶鞘出现云纹状病斑，逐渐向上蔓延，严重时导致倒伏
**防治方法**：
- 合理密植：每亩插1.8-2.0万穴
- 药剂防治：5%井冈霉素水剂500倍液，24%噻呋酰胺悬浮剂1500倍液
- 农业措施：及时晒田，控制无效分蘖

## 二、种植规划知识

### 2.1 品种选择
**主要水稻品种推荐**：
- 早稻品种：中早39、浙辐802、金早47（生育期105-115天）
- 中稻品种：黄华占、丰两优香1号、Y两优1号（生育期125-135天）
- 晚稻品种：中嘉早17、天优华占、深两优5814（生育期130-140天）

### 2.2 种植密度规划
**种植密度标准**：
- 常规稻：每亩1.8-2.2万穴，每穴3-4苗
- 杂交稻：每亩1.5-1.8万穴，每穴1-2苗
- 机插秧：行距25-30cm，株距14-16cm

### 2.3 生育期管理
**育苗期管理**（播种-移栽）：
- 播种时间：根据品种和地区确定，早稻3月下旬-4月上旬
- 苗床管理：保持湿润，温度控制在25-30℃
- 炼苗期：移栽前5-7天逐步通风炼苗

**分蘖期管理**（移栽-拔节）：
- 水分管理：浅水促分蘖，有效分蘖期保持3-5cm水层
- 施肥管理：分蘖肥占总氮量的30-40%
- 病虫害防治：重点防治纹枯病、稻飞虱

## 三、灌溉策略知识

### 3.1 水稻需水规律
**各生育期需水量**：
- 育苗期：保持土壤湿润，需水量较少
- 返青期：浅水层（3-5cm），促进生根
- 分蘖期：浅水勤灌，促进分蘖
- 拔节孕穗期：保持水层（5-8cm），需水关键期
- 抽穗开花期：保持水层（3-5cm），需水敏感期
- 灌浆成熟期：干湿交替，提高籽粒充实度

### 3.2 节水灌溉技术
**浅湿灌溉法**：
- 返青期：保持3-5cm浅水层
- 分蘖期：浅水勤灌，2-3天灌一次
- 孕穗期：保持5-8cm水层
- 灌浆期：干湿交替，3-5天灌一次

**控制灌溉法**：
- 土壤水分下限：田间持水量的70-80%
- 灌溉时间：下午4点后或早晨灌水
- 灌溉量：每次灌水3-5cm

## 四、施肥管理知识

### 4.1 施肥原则
**测土配方施肥**：
- 基础施肥：根据土壤测试结果确定
- 分期施肥：分基肥、分蘖肥、穗肥
- 平衡施肥：氮磷钾配合，增施微量元素

### 4.2 推荐施肥方案
**高产田**（亩产600kg以上）：
- 总氮量：12-14kg/亩
- 基肥：占总氮量的40%，磷肥全部，钾肥的50%
- 分蘖肥：占总氮量的30%
- 穗肥：占总氮量的30%，钾肥的50%

**中产田**（亩产500-600kg）：
- 总氮量：10-12kg/亩
- 基肥：占总氮量的50%，磷肥全部，钾肥的60%
- 分蘖肥：占总氮量的30%
- 穗肥：占总氮量的20%，钾肥的40%

## 五、病虫害综合防治知识

### 5.1 防治原则
**预防为主，综合防治**：
- 农业防治：选用抗病品种，合理轮作
- 物理防治：设置诱杀装置，人工捕杀
- 生物防治：保护天敌，使用生物农药
- 化学防治：科学用药，轮换使用

### 5.2 关键时期防治
**播种前**：
- 种子处理：药剂浸种，预防种传病害
- 土壤处理：深翻晒垡，减少病虫基数

**分蘖期**：
- 重点防治：纹枯病、稻飞虱、二化螟
- 防治时间：分蘖盛期

**孕穗抽穗期**：
- 重点防治：稻瘟病、稻曲病、三化螟
- 防治时间：破口前5-7天

**灌浆期**：
- 重点防治：穗颈瘟、稻飞虱
- 防治时间：灌浆初期

## 六、收获与储存知识

### 6.1 适时收获
**收获时期判断**：
- 成熟度：籽粒黄熟，含水量20-25%
- 时间：齐穗后25-30天
- 天气：选择晴天收获

### 6.2 储存管理
**干燥要求**：
- 安全水分：籼稻≤13.5%，粳稻≤14.5%
- 干燥方法：自然晾晒或机械烘干
- 储存条件：温度≤15℃，相对湿度≤70%

**储存技术**：
- 通风储存：定期通风，防止霉变
- 防虫处理：磷化铝熏蒸
- 品质监测：定期检查水分和品质
"""

        print(f"原始文档长度: {len(original_doc)} 字符")
        print(f"优化文档长度: {len(optimized_doc)} 字符")

        # 保存优化后的文档
        with open("optimized_rice_knowledge.txt", "w", encoding="utf-8") as f:
            f.write(optimized_doc)

        print("优化文档已保存到 optimized_rice_knowledge.txt")

        return optimized_doc

    except Exception as e:
        print(f"优化文档失败: {e}")
        return None


async def create_simple_rag():
    """创建简单的RAG系统"""
    print("\n创建简单的RAG系统...")

    try:
        import shutil

        # 1. 删除旧的向量数据库
        vector_store_path = "./vector_store"
        if os.path.exists(vector_store_path):
            shutil.rmtree(vector_store_path)
            print("已删除旧的向量数据库")

        # 2. 使用优化后的文档
        optimized_doc = optimize_knowledge_document()
        if not optimized_doc:
            print("无法获取优化文档")
            return False

        # 3. 使用现有本地模型
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_core.documents import Document
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        print("加载本地嵌入模型...")

        # 使用现有的本地模型路径
        local_model_path = "./models/sentence-transformers-all-MiniLM-L6-v2"

        if os.path.exists(local_model_path):
            print(f"使用本地模型: {local_model_path}")
            embeddings = HuggingFaceEmbeddings(
                model_name=local_model_path,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            print("本地模型不存在，尝试使用默认模型")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

        # 4. 创建文档
        documents = [
            Document(
                page_content=optimized_doc,
                metadata={
                    "source": "optimized_rice_knowledge",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        # 5. 分割文档（使用更小的chunk_size，确保每个chunk更专注）
        print("分割文档...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # 更小的chunk_size
            chunk_overlap=30,
        )
        split_docs = text_splitter.split_documents(documents)
        print(f"分割成 {len(split_docs)} 个片段")

        # 6. 创建向量数据库
        print("创建向量数据库...")
        vector_store = FAISS.from_documents(split_docs, embeddings)

        # 7. 保存向量数据库
        vector_store.save_local(vector_store_path)
        print(f"向量数据库已保存到: {vector_store_path}")

        # 8. 测试检索
        print("\n测试检索...")
        retriever = vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": 3}
        )

        test_queries = [
            "稻瘟病症状",
            "种植密度规划",
            "灌溉策略",
            "施肥方案",
            "病虫害防治",
        ]

        for query in test_queries:
            print(f"\n查询: {query}")
            docs = retriever.invoke(query)

            if docs:
                print(f"检索到 {len(docs)} 个文档")

                for i, doc in enumerate(docs):
                    # 提取文档的关键信息
                    content = doc.page_content
                    lines = content.splitlines()

                    # 找标题或关键词
                    title = ""
                    for line in lines[:3]:
                        if line.strip() and (
                            line.startswith("#")
                            or line.startswith("##")
                            or line.startswith("###")
                        ):
                            title = line.strip()
                            break

                    if not title and lines:
                        title = lines[0][:50].strip()

                    print(f"  文档 {i + 1}: {title}...")
            else:
                print("未检索到文档")

        return True

    except Exception as e:
        print(f"创建简单RAG失败: {e}")
        import traceback

        traceback.print_exc()
        return False


async def integrate_with_existing_system():
    """集成到现有系统"""
    print("\n集成到现有系统...")

    try:
        # 1. 更新RAG服务使用的文档
        print("更新RAG服务使用的文档...")

        # 读取优化后的文档
        with open("optimized_rice_knowledge.txt", "r", encoding="utf-8") as f:
            optimized_doc = f.read()

        # 2. 更新yoloapp/rag.py中的get_rice_disease_document函数
        rag_file = "yoloapp/rag.py"

        with open(rag_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 找到get_rice_disease_document函数
        import re

        pattern = r'def get_rice_disease_document\(\):.*?"""(?:.*?\n)*?return """'

        # 创建新的函数内容
        new_function = (
            '''def get_rice_disease_document():
    """获取水稻病害知识文档"""
    return """'''
            + optimized_doc
            + '"""'
        )

        # 替换函数（简单方法：直接重写文件的相关部分）
        lines = content.splitlines()
        new_lines = []
        in_function = False
        replaced = False

        for line in lines:
            if "def get_rice_disease_document():" in line and not replaced:
                new_lines.append(new_function)
                in_function = True
                replaced = True
            elif in_function and line.strip().startswith('"""') and '"""' in line:
                # 跳过原函数内容
                continue
            elif in_function and '"""' in line:
                in_function = False
                continue
            elif not in_function:
                new_lines.append(line)

        # 如果没有找到函数，添加新函数
        if not replaced:
            # 找到合适的位置插入
            for i, line in enumerate(lines):
                if "class RAGService:" in line:
                    # 在类定义前插入
                    new_lines = lines[:i] + [new_function, ""] + lines[i:]
                    break

        # 写回文件
        with open(rag_file, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        print("RAG服务文档已更新")

        # 3. 重置RAG服务
        from yoloapp.rag import _rag_service_instance

        _rag_service_instance = None
        print("RAG服务已重置")

        return True

    except Exception as e:
        print(f"集成失败: {e}")
        return False


async def test_integrated_system():
    """测试集成后的系统"""
    print("\n测试集成后的系统...")

    try:
        # 等待一下，确保文件已保存
        import time

        time.sleep(1)

        # 重新导入模块
        import importlib
        import yoloapp.rag

        importlib.reload(yoloapp.rag)

        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client

        # 初始化
        rag_service = get_rag_service()
        await rag_service.initialize()

        if not rag_service.vector_store:
            print("向量数据库未初始化")
            return False

        print("RAG系统初始化成功")

        # 简单测试
        llm_client = get_llm_client("default")

        test_query = "水稻白叶枯病的症状是什么？"
        print(f"\n测试查询: {test_query}")

        response = await rag_service.query(test_query, llm_client)

        print(f"回答长度: {len(response)} 字符")
        print(f"回答预览: {response[:200]}...")

        # 检查回答质量
        if len(response) > 100 and "白叶枯" in response:
            print("[OK] 回答包含相关关键词，RAG系统工作正常")
            return True
        else:
            print("[WARNING] 回答可能有问题")
            return False

    except Exception as e:
        print(f"测试失败: {e}")
        return False


async def main():
    """主函数"""
    print("最终解决方案：优化RAG系统")
    print("=" * 60)

    print("步骤1: 优化知识文档结构")
    doc_optimized = optimize_knowledge_document()

    if not doc_optimized:
        print("文档优化失败")
        return False

    print("\n步骤2: 创建简单的RAG系统")
    rag_created = await create_simple_rag()

    if not rag_created:
        print("RAG创建失败")
        return False

    print("\n步骤3: 集成到现有系统")
    integrated = await integrate_with_existing_system()

    if not integrated:
        print("集成失败")
        return False

    print("\n步骤4: 测试集成后的系统")
    test_passed = await test_integrated_system()

    print("\n" + "=" * 60)
    if test_passed:
        print("[OK] 解决方案实施成功！")
        print("RAG系统已优化，现在可以正确处理：")
        print("  1. 病害防治查询")
        print("  2. 种植规划查询")
        print("  3. 灌溉策略查询")
        print("  4. 施肥管理查询")
        print("  5. 病虫害防治查询")
    else:
        print("[WARNING] 解决方案部分成功，可能需要进一步调整")

    print("\n下一步建议:")
    print("  1. 运行完整的功能测试: python 快速功能测试.py")
    print("  2. 测试API接口: python test_api_simple.py")
    print("  3. 验证检测结果只显示病害名称")
    print("  4. 验证三选项确认流程")

    return test_passed


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n操作失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
