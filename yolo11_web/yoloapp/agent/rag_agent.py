# -*- coding: utf-8 -*-
"""
节点8: RAG检索 Agent
负责检索相关知识
"""

from typing import List
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError, RAGError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class RAGAgent(BaseAgent):
    """
    RAG知识检索 Agent
    
    职责:
    - 判断是否需要RAG检索
    - 执行知识检索
    - 整合检索结果
    """
    
    def __init__(self, skill_client=None):
        super().__init__(
            name="RAGAgent",
            role=AgentRole.KNOWLEDGE_RETRIEVER,
            description="负责检索相关知识"
        )
        self.skill_client = skill_client
    
    async def step(self) -> str:
        """
        执行RAG检索步骤
        
        Returns:
            检索结果描述
        """
        try:
            logger.info(f"[{self.name}] 开始知识检索...")
            
            # 1. 判断是否需要RAG
            intent = self.memory.metadata.get("intent", "chat")
            if not self._should_use_rag(intent):
                result = "⏭️ 跳过RAG检索（不需要）"
                self.memory.add_message(Message(
                    role="system",
                    content=result
                ))
                logger.info(f"[{self.name}] {result}")
                return result
            
            # 2. 构建查询
            query = self._build_query()
            
            # 3. 执行检索
            rag_result = await self._retrieve_knowledge(query)
            
            # 4. 保存结果
            rag_results = self.memory.metadata.get("rag_results", [])
            rag_results.append(rag_result)
            self.memory.metadata["rag_results"] = rag_results
            
            # 5. 记录到 Memory
            summary = f"检索完成: {len(rag_result)} 字符"
            self.memory.add_message(Message(
                role="system",
                content=summary
            ))
            
            logger.info(f"[{self.name}] {summary}")
            
            return summary
            
        except Exception as e:
            error_msg = f"知识检索失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            raise RAGError(error_msg)
    
    def _should_use_rag(self, intent: str) -> bool:
        """判断是否需要进行RAG检索"""
        # 查询意图或聊天意图需要RAG
        if intent in ["query", "chat"]:
            return True
        
        # 检测意图如果没有检测结果也可以尝试RAG
        if intent == "detect":
            tool_results = self.memory.metadata.get("tool_results", [])
            if not tool_results:
                return True
        
        return False
    
    def _build_query(self) -> str:
        """构建检索查询"""
        # 获取用户输入
        query = self._get_user_input()
        logger.info(f"[{self.name}] 用户输入: {query}")
        
        # 如果有检测结果，添加到查询中
        tool_results = self.memory.metadata.get("tool_results", [])
        logger.info(f"[{self.name}] Tool 结果数量: {len(tool_results)}")
        
        for i, result in enumerate(tool_results):
            logger.info(f"[{self.name}] Tool 结果 {i+1}: skill={result.get('skill')}, success={result.get('success')}")
            if result.get("skill") == "DetectionSkill" and result.get("success"):
                detection_result = result.get("result", "")
                logger.info(f"[{self.name}] 检测结果长度: {len(detection_result)} 字符")
                logger.info(f"[{self.name}] 检测结果内容: {detection_result[:200]}...")
                if detection_result:
                    query += f" 检测结果: {detection_result}"
                    logger.info(f"[{self.name}] 已将检测结果添加到查询")
                break
        
        logger.info(f"[{self.name}] 最终查询: {query[:200]}...")
        return query
    
    def _get_user_input(self) -> str:
        """从 Memory 中获取用户输入"""
        for msg in reversed(self.memory.messages):
            if msg.role == "user":
                return msg.content
        return ""
    
    async def _retrieve_knowledge(self, query: str) -> str:
        """检索知识 - 直接调用 RAG Service"""
        try:
            # 方法1: 尝试从 skill_client 获取 RAG service
            if self.skill_client and hasattr(self.skill_client, 'rag_service'):
                rag_service = self.skill_client.rag_service
                llm = self.skill_client.llm
                
                if rag_service and llm:
                    logger.info(f"[{self.name}] 使用 skill_client 的 RAG service")
                    result = await rag_service.query_knowledge_base(query, llm)
                    logger.info(f"[{self.name}] RAG 返回: {len(result)} 字符")
                    return result
            
            # 方法2: 尝试从 agent_factory 获取 RAG service
            try:
                from routers.agent_factory import get_rag_service, get_llm
                rag_service = await get_rag_service()
                llm = get_llm()
                
                if rag_service and llm:
                    logger.info(f"[{self.name}] 使用 agent_factory 的 RAG service")
                    result = await rag_service.query_knowledge_base(query, llm)
                    logger.info(f"[{self.name}] RAG 返回: {len(result)} 字符")
                    return result
            except Exception as e:
                logger.warning(f"[{self.name}] 无法从 agent_factory 获取 RAG: {e}")
            
            # 方法3: 降级到 KnowledgeSkill（但这会返回硬编码知识）
            if self.skill_client:
                logger.warning(f"[{self.name}] 降级到 KnowledgeSkill（硬编码知识）")
                result = await self.skill_client.call_capability(
                    "KnowledgeSkill",
                    "query_knowledge",
                    question=query
                )
                return str(result) if result else "未找到相关知识"
            
            return "暂无可用的知识检索服务"
            
        except Exception as e:
            logger.error(f"[{self.name}] 知识检索失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"知识检索失败: {str(e)}"
