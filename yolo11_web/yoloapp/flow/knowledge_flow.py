# -*- coding: utf-8 -*-
"""
知识查询流程

编排知识查询相关的 Agent，完成知识检索和回答生成。
"""

from typing import Dict, Any, Optional, List

from yoloapp.flow.base import BaseFlow
from yoloapp.agent.knowledge_agent import KnowledgeAgent
from yoloapp.exceptions import FlowError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeFlow(BaseFlow):
    """知识查询流程
    
    完整的知识查询流程包括：
    1. 知识检索（KnowledgeAgent）
    2. 结果整理
    3. 回答生成
    
    Attributes:
        top_k: 检索结果数量
        min_relevance: 最小相关度阈值
    """
    
    top_k: int = 5
    min_relevance: float = 0.0
    
    def __init__(self, **kwargs):
        """初始化知识查询流程
        
        Args:
            **kwargs: 其他参数
        """
        if "name" not in kwargs:
            kwargs["name"] = "knowledge_flow"
        if "description" not in kwargs:
            kwargs["description"] = "知识查询和回答生成流程"
        
        super().__init__(**kwargs)
        
        # 创建并添加 Agent
        self._setup_agents()
        
        logger.info(f"知识查询流程 {self.name} 初始化成功")
    
    def _setup_agents(self) -> None:
        """设置 Agent"""
        try:
            # 创建知识 Agent
            knowledge_agent = KnowledgeAgent(
                top_k=self.top_k
            )
            self.add_agent("knowledge", knowledge_agent)
            
            # 设置主 Agent
            self.set_primary_agent("knowledge")
            
            logger.info("知识查询流程 Agent 设置完成")
        
        except Exception as e:
            logger.error(f"设置 Agent 失败: {e}")
            raise FlowError(
                message=f"知识查询流程初始化失败: {str(e)}",
                error_code="FLOW_SETUP_FAILED",
                context={"error": str(e)}
            )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行知识查询流程
        
        Args:
            input_data: 输入数据，包含：
                - query: 查询文本（必需）
                - top_k: 检索结果数量（可选）
                - context: 额外上下文（可选）
                
        Returns:
            执行结果字典，包含：
                - query: 原始查询
                - knowledge: 知识检索结果
                - answer: 生成的回答
                - summary: 结果摘要
                
        Raises:
            FlowError: 流程执行失败
        """
        # 验证输入
        query = input_data.get("query")
        if not query:
            raise FlowError(
                message="缺少必需参数: query",
                error_code="MISSING_QUERY",
                context=input_data
            )
        
        top_k = input_data.get("top_k", self.top_k)
        context = input_data.get("context", "")
        
        result = {
            "query": query,
            "knowledge": None,
            "answer": "",
            "summary": ""
        }
        
        try:
            # 步骤 1: 执行知识检索
            logger.info(f"步骤 1: 执行知识检索 - {query}")
            knowledge_agent = self.require_agent("knowledge")
            
            # 设置检索参数
            knowledge_agent.set_top_k(top_k)
            
            # 构建完整查询（包含上下文）
            full_query = self._build_full_query(query, context)
            
            # 执行检索
            knowledge_summary = await knowledge_agent.run(full_query)
            knowledge_result = knowledge_agent.get_knowledge_result()
            
            result["knowledge"] = knowledge_result
            logger.info(f"知识检索完成: {knowledge_result}")
            
            # 步骤 2: 生成回答
            logger.info("步骤 2: 生成回答")
            answer = self._generate_answer(query, knowledge_result, context)
            result["answer"] = answer
            
            # 步骤 3: 生成摘要
            result["summary"] = self._generate_summary(result)
            
            logger.info("知识查询流程执行完成")
            return result
        
        except Exception as e:
            error_msg = f"知识查询流程执行失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FlowError(
                message=error_msg,
                error_code="KNOWLEDGE_FLOW_FAILED",
                context={
                    "query": query,
                    "error": str(e),
                    "partial_result": result
                }
            )
    
    def _build_full_query(self, query: str, context: str) -> str:
        """构建完整查询
        
        Args:
            query: 原始查询
            context: 额外上下文
            
        Returns:
            完整查询文本
        """
        if not context:
            return query
        
        return f"{context}\n\n{query}"
    
    def _generate_answer(
        self,
        query: str,
        knowledge_result: Optional[Dict[str, Any]],
        context: str
    ) -> str:
        """生成回答
        
        Args:
            query: 原始查询
            knowledge_result: 知识检索结果
            context: 额外上下文
            
        Returns:
            生成的回答
        """
        if not knowledge_result or knowledge_result.get("count", 0) == 0:
            return self._get_default_answer(query)
        
        # 提取知识内容
        documents = knowledge_result.get("documents", [])
        if not documents:
            return self._get_default_answer(query)
        
        # 整理知识内容
        knowledge_texts = []
        for i, doc in enumerate(documents[:3], 1):  # 只使用前 3 条
            if isinstance(doc, dict):
                content = doc.get("content", str(doc))
            else:
                content = str(doc)
            
            # 截断过长的内容
            if len(content) > 300:
                content = content[:300] + "..."
            
            knowledge_texts.append(f"{i}. {content}")
        
        # 构建回答
        answer_parts = [
            f"根据相关知识，关于「{query}」的回答如下：\n",
            "\n".join(knowledge_texts)
        ]
        
        # 添加建议
        if any(keyword in query for keyword in ["防治", "治疗", "处理", "怎么办"]):
            answer_parts.append(
                "\n\n[INFO] 建议：\n"
                "1. 及时采取防治措施\n"
                "2. 加强田间管理\n"
                "3. 必要时咨询专业人员"
            )
        
        return "\n".join(answer_parts)
    
    def _get_default_answer(self, query: str) -> str:
        """获取默认回答
        
        Args:
            query: 查询文本
            
        Returns:
            默认回答
        """
        # 根据查询类型提供不同的默认回答
        if any(keyword in query for keyword in ["病", "害", "防治"]):
            return (
                "关于水稻病害的一般建议：\n\n"
                "1. 🌾 选用抗病品种\n"
                "2. [WATER] 合理灌溉，避免积水\n"
                "3. 🌱 适量施肥，增强抗性\n"
                "4. [SEARCH] 定期检查，及早发现\n"
                "5. 💊 必要时使用适当农药\n\n"
                "建议上传病害图片以获得更准确的诊断和建议。"
            )
        
        return (
            "抱歉，暂时没有找到相关知识。\n\n"
            "您可以：\n"
            "1. 尝试换个方式提问\n"
            "2. 上传病害图片进行检测\n"
            "3. 咨询专业农技人员"
        )
    
    def _generate_summary(self, result: Dict[str, Any]) -> str:
        """生成结果摘要
        
        Args:
            result: 执行结果
            
        Returns:
            摘要文本
        """
        lines = []
        
        # 查询摘要
        query = result.get("query", "")
        lines.append(f"[DETAIL] 查询: {query[:50]}...")
        
        # 知识检索摘要
        knowledge = result.get("knowledge")
        if knowledge:
            count = knowledge.get("count", 0)
            if count > 0:
                lines.append(f"📚 找到 {count} 条相关知识")
            else:
                lines.append("📚 未找到相关知识")
        
        # 回答摘要
        answer = result.get("answer", "")
        if answer:
            lines.append(f"💬 生成回答 ({len(answer)} 字符)")
        
        return "\n".join(lines)
    
    def set_top_k(self, top_k: int) -> None:
        """设置检索结果数量
        
        Args:
            top_k: 结果数量
        """
        self.top_k = top_k
        
        # 更新知识 Agent 的 top_k
        knowledge_agent = self.get_agent("knowledge")
        if knowledge_agent:
            knowledge_agent.set_top_k(top_k)
        
        logger.info(f"设置检索结果数量: {top_k}")
    
    def set_min_relevance(self, min_relevance: float) -> None:
        """设置最小相关度阈值
        
        Args:
            min_relevance: 最小相关度 (0-1)
        """
        if not 0 <= min_relevance <= 1:
            raise ValueError("最小相关度必须在 0-1 之间")
        
        self.min_relevance = min_relevance
        logger.info(f"设置最小相关度阈值: {min_relevance}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"KnowledgeFlow(agents={len(self.agents)}, top_k={self.top_k})"


# 工厂函数
def create_knowledge_flow(
    top_k: int = 5,
    min_relevance: float = 0.0
) -> KnowledgeFlow:
    """创建知识查询流程实例
    
    Args:
        top_k: 检索结果数量
        min_relevance: 最小相关度阈值
        
    Returns:
        KnowledgeFlow 实例
    """
    return KnowledgeFlow(
        top_k=top_k,
        min_relevance=min_relevance
    )
