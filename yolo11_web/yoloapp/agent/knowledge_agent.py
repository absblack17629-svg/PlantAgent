# -*- coding: utf-8 -*-
"""
知识 Agent

负责知识查询和建议生成。
"""

import asyncio
from typing import Optional, Dict, Any, List

from yoloapp.agent.base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import RAGError, RetrievalError
from yoloapp.utils.logger import get_logger

# 使用新的 yoloapp 导入
from yoloapp.rag import RAGService

logger = get_logger(__name__)


class KnowledgeAgent(BaseAgent):
    """知识 Agent
    
    专门负责知识查询和建议生成，使用 RAG 系统检索相关知识。
    
    Attributes:
        rag_service: RAG 服务实例
        top_k: 检索结果数量
        current_query: 当前查询
        knowledge_result: 知识检索结果
    """
    
    rag_service: Optional[RAGService] = None
    top_k: int = 5
    current_query: Optional[str] = None
    knowledge_result: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        """初始化知识 Agent
        
        Args:
            **kwargs: 其他参数
        """
        # 设置默认值
        if "name" not in kwargs:
            kwargs["name"] = "knowledge_agent"
        if "role" not in kwargs:
            kwargs["role"] = AgentRole.KNOWLEDGE
        if "description" not in kwargs:
            kwargs["description"] = "负责知识查询和建议生成"
        
        super().__init__(**kwargs)
        
        # 初始化 RAG 服务
        try:
            self.rag_service = RAGService()
            logger.info(f"知识 Agent {self.name} 初始化成功")
        except Exception as e:
            logger.error(f"知识 Agent {self.name} 初始化失败: {e}")
            # RAG 服务失败不应该阻止 Agent 创建
            self.rag_service = None
    
    async def step(self) -> str:
        """执行知识查询步骤
        
        Returns:
            步骤执行结果
            
        Raises:
            RAGError: 如果查询失败
        """
        # 获取最后一条用户消息
        last_user_msg = self.memory.get_last_user_message()
        if not last_user_msg:
            self.mark_finished()
            return "没有待处理的查询"
        
        # 提取查询
        if not self.current_query:
            self.current_query = last_user_msg.content
        
        # 执行知识检索
        try:
            logger.info(f"开始知识检索: {self.current_query}")
            
            if not self.rag_service:
                # 如果 RAG 服务不可用，返回默认建议
                result_text = self._get_default_advice()
                self.update_memory("assistant", result_text)
                self.mark_finished()
                return f"使用默认建议: {result_text}"
            
            # 在线程池中执行检索
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._retrieve_sync,
                self.current_query
            )
            
            self.knowledge_result = result
            
            # 格式化结果
            result_text = self._format_knowledge_result(result)
            self.update_memory("assistant", result_text)
            
            # 标记完成
            self.mark_finished()
            
            logger.info(f"知识检索完成: 找到 {len(result.get('documents', []))} 条相关知识")
            return f"知识检索完成: {result_text[:100]}..."
        
        except Exception as e:
            error_msg = f"知识检索失败: {str(e)}"
            logger.error(error_msg)
            
            # 降级到默认建议
            default_advice = self._get_default_advice()
            self.update_memory("assistant", f"{error_msg}\n\n{default_advice}")
            self.mark_finished()
            
            return f"检索失败，使用默认建议"
    
    def _retrieve_sync(self, query: str) -> Dict[str, Any]:
        """同步检索方法
        
        Args:
            query: 查询文本
            
        Returns:
            检索结果字典
            
        Raises:
            RetrievalError: 如果检索失败
        """
        try:
            # 执行检索
            results = self.rag_service.search(query, top_k=self.top_k)
            
            return {
                "query": query,
                "documents": results if results else [],
                "count": len(results) if results else 0
            }
        
        except Exception as e:
            logger.error(f"同步检索失败: {e}")
            raise RetrievalError(query=query, cause=e)
    
    def _format_knowledge_result(self, result: Dict[str, Any]) -> str:
        """格式化知识检索结果
        
        Args:
            result: 检索结果字典
            
        Returns:
            格式化的结果文本
        """
        if result["count"] == 0:
            return self._get_default_advice()
        
        lines = [f"找到 {result['count']} 条相关知识:\n"]
        
        for i, doc in enumerate(result["documents"][:3], 1):  # 只显示前 3 条
            # 假设文档是字符串或字典
            if isinstance(doc, dict):
                content = doc.get("content", str(doc))
            else:
                content = str(doc)
            
            # 截断过长的内容
            if len(content) > 200:
                content = content[:200] + "..."
            
            lines.append(f"{i}. {content}\n")
        
        return "\n".join(lines)
    
    def _get_default_advice(self) -> str:
        """获取默认建议
        
        Returns:
            默认建议文本
        """
        return (
            "建议采取以下措施:\n"
            "1. 及时清除病叶和病株\n"
            "2. 加强田间管理，保持通风\n"
            "3. 合理施肥，增强植株抗性\n"
            "4. 必要时使用适当的农药防治\n"
            "5. 定期监测病情发展"
        )
    
    def set_top_k(self, top_k: int) -> None:
        """设置检索结果数量
        
        Args:
            top_k: 结果数量
        """
        if top_k < 1:
            raise ValueError("top_k 必须大于 0")
        
        self.top_k = top_k
        logger.info(f"设置检索结果数量: {top_k}")
    
    def get_knowledge_result(self) -> Optional[Dict[str, Any]]:
        """获取知识检索结果
        
        Returns:
            检索结果字典，如果未检索则返回 None
        """
        return self.knowledge_result
    
    def reset(self) -> None:
        """重置 Agent"""
        super().reset()
        self.current_query = None
        self.knowledge_result = None
        logger.info(f"知识 Agent {self.name} 已重置")
