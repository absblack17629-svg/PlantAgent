# -*- coding: utf-8 -*-
"""
RAG知识库服务
负责检索增强生成和知识库管理
"""

import os
import traceback
from typing import Optional, List, Dict
from datetime import datetime

# 修复导入：使用新的 langchain_text_splitters 包
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    # 降级方案：尝试旧的导入路径
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        print("[FAILURE] 无法导入 RecursiveCharacterTextSplitter")
        print("[INFO] 请安装: pip install langchain-text-splitters")
        RecursiveCharacterTextSplitter = None

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS

# 尝试导入 HuggingFaceEmbeddings，提供降级方案
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    print("[WARNING] langchain_huggingface 未安装，尝试备用方案...")
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        HUGGINGFACE_AVAILABLE = True
        print("[SUCCESS] 使用 langchain_community.embeddings.HuggingFaceEmbeddings")
    except ImportError:
        HUGGINGFACE_AVAILABLE = False
        print("[FAILURE] HuggingFaceEmbeddings 不可用")
        print("[INFO] 请运行: pip install langchain-huggingface sentence-transformers")

import config


def get_rice_disease_document():
    """获取水稻病害知识文档"""
    return """
水稻病害防治知识：

一、常见病害识别
1. 稻瘟病：叶片上有椭圆形或纺锤形病斑，中央灰白色，边缘褐色
2. 白叶枯病：叶片上出现黄绿色水渍状病斑，后变黄白色
3. 纹枯病：叶片基部出现褐色病斑，从下往上蔓延
4. 细菌性条斑病：叶片上出现黄绿色条斑，逐渐变褐
5. 稻曲病：穗部出现墨绿色粉状物
6. 恶苗病：植株徒长，叶片淡黄
7. 南方黑条矮缩病：植株矮化，叶片皱缩

二、常见虫害识别
1. 稻飞虱：吸食稻株汁液，导致叶片发黄
2. 稻纵卷叶螟：幼虫卷叶取食
3. 二化螟：蛀食稻茎
4. 三化螟：危害穗部
5. 稻蓟马：吸食叶片汁液

三、防治措施
1. 种子处理：用药剂浸种或温汤浸种
2. 土壤消毒：轮作倒茬，避免连作
3. 肥水管理：合理施肥，避免过量氮肥
4. 药剂防治：发病初期及时喷药
5. 品种选择：选择抗病品种

四、农业防治
1. 加强田间管理，及时清除病残体
2. 合理密植，改善通风条件
3. 适时灌溉，避免田间积水过久
4. 增施有机肥，提高植株抗病能力

五、具体病害防治方法

稻瘟病防治：
- 选用抗病品种如粤晶丝苗2号、黄华占等
- 用咪鲜胺或三环唑浸种
- 发病初期喷施稻瘟灵、三环唑、富士一号
- 合理施肥，避免偏施氮肥

白叶枯病防治：
- 选用抗病品种
- 用中生菌素或噻霉酮浸种
- 发病初期喷施叶枯唑、农用链霉素
- 避免串灌漫灌

纹枯病防治：
- 合理密植，改善通风
- 发病初期井冈霉素、苯醚甲环唑
- 清除田间病残体

稻飞虱防治：
- 选用抗虫品种
- 吡虫啉、噻嗪酮防治
- 保护天敌如蜘蛛、黑肩绿盲蝽
"""


class RAGService:
    """RAG知识库服务 - 异步版本"""

    def __init__(self, embeddings=None):
        self.vector_store = None
        self.embeddings = embeddings
        self.rag_chain = None
        self._initialized = False

    async def initialize(self):
        """初始化RAG系统（init_async的别名，用于兼容性）"""
        return await self.init_async()

    async def init_async(self):
        """异步初始化RAG系统"""
        if self._initialized:
            return

        # 检查 HuggingFaceEmbeddings 是否可用
        if not HUGGINGFACE_AVAILABLE:
            print("[FAILURE] RAG系统初始化失败：HuggingFaceEmbeddings 不可用")
            print("[INFO] 请运行安装脚本: install_rag_dependencies.bat")
            print("[INFO] 或手动安装: pip install langchain-huggingface sentence-transformers")
            return

        try:
            print("[SEARCH] 初始化RAG检索增强生成系统...")

            # 检查sentence-transformers是否可用
            try:
                import sentence_transformers

                print("[SUCCESS] sentence-transformers库已安装")
            except ImportError:
                print("[WARNING] sentence-transformers未安装，尝试自动安装...")
                import subprocess
                import sys

                try:
                    subprocess.check_call(
                        [
                            sys.executable,
                            "-m",
                            "pip",
                            "install",
                            "sentence-transformers==3.0.1",
                        ]
                    )
                    print("[SUCCESS] sentence-transformers安装成功")
                    import sentence_transformers
                except Exception as install_e:
                    print(f"[FAILURE] sentence-transformers安装失败: {str(install_e)}")
                    print("[INFO] RAG系统将使用离线模式或禁用")
                    self.embeddings = None
                    return

            # 初始化嵌入模型
            if self.embeddings is None:
                await self._init_embeddings()

            # 加载或创建知识库
            await self._load_knowledge_base()

            # 构建RAG链
            self._build_rag_chain()

            self._initialized = True
            print("[SUCCESS] RAG系统初始化成功")

        except Exception as e:
            print(f"[FAILURE] RAG系统初始化失败：{str(e)}")
            print("[INFO] RAG系统已禁用，但核心功能仍可用")
            import traceback
            traceback.print_exc()

    async def _init_embeddings(self):
        """异步初始化嵌入模型"""
        try:
            print("🤖 加载嵌入模型...")
            model_name = config.RAG_CONFIG.get(
                "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
            )
            offline_mode = config.RAG_CONFIG.get("offline_mode", False)
            
            # 转换为绝对路径（如果是本地路径）
            if model_name.startswith("./") or model_name.startswith("models/"):
                import os
                model_name = os.path.abspath(model_name)
                print(f"[FILE] 使用本地模型: {model_name}")
            else:
                print(f"🌐 使用在线模型: {model_name}")

            # 在线程池中加载模型（避免阻塞事件循环）
            import asyncio

            loop = asyncio.get_event_loop()

            def load_embeddings():
                return HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True}
                )

            self.embeddings = await loop.run_in_executor(None, load_embeddings)
            print("[SUCCESS] 嵌入模型加载成功")

        except Exception as embed_e:
            print(f"[FAILURE] 嵌入模型加载失败：{str(embed_e)}")
            print("[INFO] 可能原因：")
            print("   • 网络连接问题，无法下载模型")
            print("   • 模型文件损坏或路径错误")
            print("   • 磁盘空间不足")
            print("[DETAIL] 将尝试使用本地缓存或降级模式")
            import traceback
            traceback.print_exc()
            self.embeddings = None

    async def _load_knowledge_base(self):
        """异步加载知识库"""
        try:
            vector_store_path = config.RAG_CONFIG.get(
                "vector_store_path", "./vector_store"
            )

            # 在线程池中加载向量存储（避免阻塞）
            import asyncio

            loop = asyncio.get_event_loop()

            # 尝试从本地加载现有的向量存储
            if os.path.exists(vector_store_path):
                try:

                    def load_vector_store():
                        return FAISS.load_local(
                            vector_store_path,
                            self.embeddings,
                            allow_dangerous_deserialization=True,
                        )

                    self.vector_store = await loop.run_in_executor(
                        None, load_vector_store
                    )
                    print("[SUCCESS] 已加载现有知识库")
                except Exception as load_error:
                    print(f"[WARNING] 现有知识库文件损坏或不完整：{str(load_error)}")
                    print("🗑️ 删除损坏的向量存储目录，准备重新创建...")
                    import shutil

                    await loop.run_in_executor(
                        None, lambda: shutil.rmtree(vector_store_path)
                    )
                    self.vector_store = None
                    print("[SUCCESS] 已清理损坏的知识库，将创建新的知识库")
            else:
                # 创建空的向量存储
                self.vector_store = None
                print("[WARNING] 未找到现有知识库，将创建新的知识库")

            # 加载初始农业知识文档
            await self._load_initial_documents()

        except Exception as e:
            print(f"[FAILURE] 知识库加载失败：{str(e)}")
            self.vector_store = None

    async def _load_initial_documents(self):
        """异步加载初始文档到知识库"""
        rice_disease_doc = get_rice_disease_document()

        # 创建文档对象
        documents = [
            Document(
                page_content=rice_disease_doc,
                metadata={
                    "source": "rice_disease_manual",
                    "type": "agricultural_knowledge",
                },
            )
        ]

        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.RAG_CONFIG.get("chunk_size", 500),
            chunk_overlap=config.RAG_CONFIG.get("chunk_overlap", 50),
        )
        split_docs = text_splitter.split_documents(documents)

        # 在线程池中创建/更新向量存储
        import asyncio

        loop = asyncio.get_event_loop()

        def create_or_update_vector_store():
            if self.vector_store is None:
                return FAISS.from_documents(split_docs, self.embeddings)
            else:
                self.vector_store.add_documents(split_docs)
                return self.vector_store

        self.vector_store = await loop.run_in_executor(
            None, create_or_update_vector_store
        )

        # 保存向量存储
        vector_store_path = config.RAG_CONFIG.get("vector_store_path", "./vector_store")
        os.makedirs(vector_store_path, exist_ok=True)

        await loop.run_in_executor(
            None, lambda: self.vector_store.save_local(vector_store_path)
        )

        print("[SUCCESS] 农业知识文档已添加到RAG知识库")

    def _build_rag_chain(self):
        """构建RAG问答链 - 不再在初始化时构建，改为查询时动态构建"""
        # 这个方法现在只是一个占位符，实际的RAG链在query_knowledge_base中动态构建
        # 这样可以使用传入的llm参数，而不是依赖self.llm
        pass

    async def query(self, question: str, llm=None) -> str:
        """
        异步RAG知识库问答（query_knowledge_base的别名，用于兼容性）

        Args:
            question: 用户问题
            llm: 大语言模型实例（LLMClient 或 LangChain LLM）

        Returns:
            回答内容
        """
        return await self.query_knowledge_base(question, llm)
    
    async def query_knowledge_base(self, question: str, llm=None) -> str:
        """
        异步RAG知识库问答

        Args:
            question: 用户问题
            llm: 大语言模型实例（LLMClient 或 LangChain LLM）

        Returns:
            回答内容
        """
        print(f"收到知识库查询：{question}")

        # 确保RAG系统已初始化
        await self.init_async()

        # 检查RAG系统是否可用
        if not self.vector_store or not llm:
            print("RAG系统未初始化，返回默认回答")
            return "抱歉，知识库系统暂未初始化，请稍后重试。"

        try:
            # 执行RAG问答
            print("正在检索相关知识...")
            print("正在生成答案...")
            import time

            start_time = time.time()

            # 创建检索器
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": config.RAG_CONFIG.get("top_k", 3)},
            )

            # 先检索文档，查看检索结果
            retrieved_docs = await retriever.ainvoke(question)
            print(f"📄 检索到 {len(retrieved_docs)} 个相关文档片段")
            for i, doc in enumerate(retrieved_docs, 1):
                content_preview = doc.page_content[:150].replace('\n', ' ')
                source = doc.metadata.get('source', 'unknown')
                print(f"   片段 {i} (来源: {source}): {content_preview}...")

            # 检查 llm 类型，如果是 LLMClient，直接调用而不使用 LangChain 链
            from yoloapp.llm import LLMClient
            if isinstance(llm, LLMClient):
                # 使用 LLMClient 直接调用
                from yoloapp.prompt import RAG_SYSTEM_PROMPT, RAG_QA_TEMPLATE
                from yoloapp.schema import Message
                
                # 构建上下文
                context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
                
                # 构建提示
                full_prompt = RAG_QA_TEMPLATE.format(context=context_text, question=question)
                
                # 调用 LLM（使用系统提示词）
                messages = [
                    Message.system_message(RAG_SYSTEM_PROMPT),
                    Message.user_message(full_prompt)
                ]
                response = await llm.ask(messages)
                
                # 记录执行结果
                elapsed_time = time.time() - start_time
                print(f"RAG问答完成，耗时：{elapsed_time:.2f}秒")
                print(f"生成答案长度：{len(response)} 字符")
                print(f"生成答案预览：{response[:200]}{'...' if len(response) > 200 else ''}")
                
                return response
            else:
                # 使用 LangChain 链（兼容 LangChain LLM）
                from yoloapp.prompt import RAG_SYSTEM_PROMPT, RAG_QA_TEMPLATE
                from langchain_core.prompts import ChatPromptTemplate
                from langchain_core.runnables import RunnablePassthrough
                from langchain_core.output_parsers import StrOutputParser

                # 创建包含系统提示词的提示模板
                rag_prompt = ChatPromptTemplate.from_messages([
                    ("system", RAG_SYSTEM_PROMPT),
                    ("user", RAG_QA_TEMPLATE)
                ])
                
                rag_chain = (
                    {"context": retriever, "question": RunnablePassthrough()}
                    | rag_prompt
                    | llm
                    | StrOutputParser()
                )

                # 使用异步方法调用
                response = await rag_chain.ainvoke(question)
                
                # 调试：检查响应类型和内容
                print(f"[SEARCH] 响应类型: {type(response)}")
                print(f"[SEARCH] 响应内容: {repr(response)}")
                
                # 处理不同类型的响应
                if hasattr(response, 'content'):
                    response_text = response.content
                elif hasattr(response, '__str__') and str(response):
                    response_text = str(response)
                elif isinstance(response, dict) and 'content' in response:
                    response_text = response['content']
                elif isinstance(response, str):
                    response_text = response
                else:
                    response_text = str(response)
                
                # 记录执行结果
                elapsed_time = time.time() - start_time
                print(f"RAG问答完成，耗时：{elapsed_time:.2f}秒")
                print(f"生成答案长度：{len(response_text)} 字符")
                print(f"生成答案预览：{response_text[:200]}{'...' if len(response_text) > 200 else ''}")
                
                return response_text

        except Exception as e:
            print(f"RAG问答过程中出现错误：{str(e)}")
            return "抱歉，知识库查询出现异常，请稍后重试。"

    async def analyze_detection_results(
        self, question: str, detections: List[Dict], llm=None
    ) -> str:
        """
        异步智能分析检测结果和用户问题

        Args:
            question: 用户问题
            detections: 检测结果
            llm: 大语言模型实例

        Returns:
            分析结果
        """
        if not llm:
            return "AI分析功能暂不可用"

        try:
            # 构建分析提示
            if detections:
                detect_summary = "检测结果统计："
                target_count = {}
                for item in detections:
                    target_type = item["类别"]
                    target_count[target_type] = target_count.get(target_type, 0) + 1

                for target, count in target_count.items():
                    detect_summary += f"{target}={count}个；"
                detect_summary = detect_summary.rstrip("；")
            else:
                detect_summary = "未检测到目标"

            analysis_prompt = DETECTION_ANALYSIS_TEMPLATE.format(
                detect_summary=detect_summary,
                detections=detections,
                question=question or "请分析检测结果",
            )

            # 使用LangChain异步生成分析
            response = await llm.ainvoke(analysis_prompt)
            return response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            print(f"[FAILURE] 检测结果分析失败：{str(e)}")
            return "检测结果分析失败，请查看原始检测数据"

    async def add_knowledge_document(self, content: str, metadata: Dict = None):
        """
        异步添加文档到知识库

        Args:
            content: 文档内容
            metadata: 元数据

        Returns:
            是否成功
        """
        # 确保RAG系统已初始化
        await self.init_async()

        if not self.vector_store or not self.embeddings:
            print("[FAILURE] 知识库未初始化，无法添加文档")
            return False

        try:
            # 创建文档对象
            doc = Document(
                page_content=content,
                metadata=metadata or {"source": "user_input", "type": "custom"},
            )

            # 分割文档
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=config.RAG_CONFIG.get("chunk_size", 500),
                chunk_overlap=config.RAG_CONFIG.get("chunk_overlap", 50),
            )
            split_docs = text_splitter.split_documents([doc])

            # 在线程池中添加文档，添加超时保护
            import asyncio

            loop = asyncio.get_event_loop()

            try:
                await asyncio.wait_for(
                    loop.run_in_executor(
                        None, lambda: self.vector_store.add_documents(split_docs)
                    ),
                    timeout=5.0,  # 5秒超时
                )
            except asyncio.TimeoutError:
                print("[WARNING] 添加文档到向量库超时")
                return False
            except asyncio.CancelledError:
                print("[WARNING] 添加文档操作被取消")
                return False

            # 保存更新，添加超时保护
            vector_store_path = config.RAG_CONFIG.get(
                "vector_store_path", "./vector_store"
            )
            try:
                await asyncio.wait_for(
                    loop.run_in_executor(
                        None, lambda: self.vector_store.save_local(vector_store_path)
                    ),
                    timeout=5.0,  # 5秒超时
                )
            except asyncio.TimeoutError:
                print("[WARNING] 保存向量库超时，但文档已添加到内存")
                return True  # 文档已添加，只是保存失败
            except asyncio.CancelledError:
                print("[WARNING] 保存向量库操作被取消")
                return True  # 文档已添加，只是保存失败

            print("[SUCCESS] 文档已添加到知识库")
            return True
        except asyncio.CancelledError:
            print("[WARNING] 添加文档操作被取消")
            return False
        except Exception as e:
            print(f"[FAILURE] 添加文档失败：{str(e)}")
            return False


# 单例实例
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例
    
    Returns:
        RAGService 实例
    """
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
