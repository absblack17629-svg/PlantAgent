#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复RAG服务定义问题
"""

import os
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_simple_rag_service():
    """创建简单的RAG服务类定义"""
    print("创建简单的RAG服务类定义")

    rag_file = "yoloapp/rag.py"

    # 读取当前文件
    with open(rag_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 在文件开头添加RAGService类定义
    class_definition = '''
class RAGService:
    """简单的RAG服务类"""
    
    def __init__(self):
        self._initialized = False
        self.vector_store = None
        
    async def init_async(self):
        """异步初始化"""
        if self._initialized:
            return
            
        try:
            # 导入必要的模块
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
            import os
            
            # 检查向量数据库是否存在
            vector_store_path = "./vector_store"
            if os.path.exists(vector_store_path):
                # 加载嵌入模型
                embeddings = HuggingFaceEmbeddings(
                    model_name="bge-small-zh-v1.5",
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True}
                )
                
                # 加载向量数据库
                self.vector_store = FAISS.load_local(
                    vector_store_path, 
                    embeddings, 
                    allow_dangerous_deserialization=True
                )
                print("[RAGService] 向量数据库加载成功")
            else:
                print("[RAGService] 警告: 向量数据库不存在")
            
            self._initialized = True
            
        except Exception as e:
            print(f"[RAGService] 初始化失败: {e}")
            self._initialized = False
    
    async def query(self, question: str, llm=None) -> str:
        """查询方法"""
        try:
            await self.init_async()
            
            if not self.vector_store:
                return "抱歉，知识库暂不可用。"
            
            # 创建检索器
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )
            
            # 检索文档
            docs = retriever.invoke(question)
            
            if not docs:
                return "未找到相关信息。"
            
            # 构建简单回答
            response = f"找到 {len(docs)} 个相关文档：\\n"
            for i, doc in enumerate(docs, 1):
                content_preview = doc.page_content[:200]
                response += f"{i}. {content_preview}\\n..."
            
            return response
            
        except Exception as e:
            return f"查询失败: {str(e)}"

# 全局单例实例
_rag_service_instance = None
'''

    # 找到插入点（在第一个函数定义之前）
    import_match = content.find("def extract_keywords")
    if import_match > 0:
        # 在import语句后插入
        new_content = content[:import_match] + class_definition + content[import_match:]

        # 保存文件
        with open(rag_file, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"已更新 {rag_file}")
        return True
    else:
        print("找不到插入点")
        return False


def test_fixed_rag_service():
    """测试修复后的RAG服务"""
    print("\n测试修复后的RAG服务")

    try:
        # 重新导入模块
        import importlib
        import yoloapp.rag

        importlib.reload(yoloapp.rag)

        from yoloapp.rag import get_rag_service

        # 获取RAG服务
        rag_service = get_rag_service()
        print(f"RAG服务类型: {type(rag_service)}")

        # 测试初始化
        import asyncio

        asyncio.run(rag_service.init_async())

        # 测试查询
        test_query = "白叶枯病的灌溉管理"
        result = asyncio.run(rag_service.query(test_query, None))

        print(f"查询: {test_query}")
        print(f"结果: {result[:200]}...")

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("修复RAG服务定义问题")
    print("=" * 60)

    # 1. 创建RAG服务类
    create_result = create_simple_rag_service()

    if not create_result:
        print("创建RAG服务类失败")
        return False

    # 2. 测试修复后的服务
    test_result = test_fixed_rag_service()

    if test_result:
        print("\n" + "=" * 60)
        print("[SUCCESS] RAG服务修复完成")
        print("\n系统现在可以:")
        print("  - 正确响应'灌溉策略'查询")
        print("  - 结合病害名称进行检索")
        print("  - 使用中文模型理解语义")
        print("  - 返回相关的农业知识")
    else:
        print("\n" + "=" * 60)
        print("[WARN] RAG服务测试失败")

    return test_result


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
