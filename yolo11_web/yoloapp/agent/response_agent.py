# -*- coding: utf-8 -*-
"""
节点9: 响应生成 Agent
负责生成最终回复
"""

import re
from typing import Dict, List
from .base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)

# 病害名称映射
DISEASE_NAME_MAP = {
    "Bacterialblight": "细菌性条斑病",
    "Browspot": "褐斑病",
    "Blast": "稻瘟病",
    "Leafblast": "叶瘟",
    "Neckblast": "穗颈瘟",
    "Sheathblight": "纹枯病",
    "Ricehispa": "稻负泥虫",
    "Tungro": "东格鲁病",
}


class ResponseAgent(BaseAgent):
    """
    响应生成 Agent
    
    职责:
    - 整合所有处理结果
    - 生成用户友好的回复
    - 处理情感和语气
    """
    
    def __init__(self):
        super().__init__(
            name="ResponseAgent",
            role=AgentRole.RESPONSE_GENERATOR,
            description="负责生成最终回复"
        )
    
    async def step(self) -> str:
        """
        执行响应生成步骤
        
        Returns:
            最终响应文本
        """
        try:
            logger.info(f"[{self.name}] 开始生成响应...")
            
            # 检查意图类型
            intent = self.memory.metadata.get("intent", "chat")
            
            # 对于普通对话，直接使用 LLM 生成回复
            if intent == "chat":
                logger.info(f"[{self.name}] 检测到普通对话，使用 LLM 直接生成...")
                response = await self._generate_chat_response()
            else:
                # 其他意图使用规则组装
                response = self._build_response()
                response = self._add_emotion(response)
            
            # 保存到 metadata
            self.memory.metadata["response"] = response
            
            # 记录到 Memory
            self.memory.add_message(Message(
                role="assistant",
                content=response
            ))
            
            logger.info(f"[{self.name}] 响应生成完成: {len(response)} 字符")
            
            return response
            
        except Exception as e:
            error_msg = f"响应生成失败: {str(e)}"
            logger.error(f"[{self.name}] {error_msg}")
            # 返回默认错误响应
            return "抱歉，处理过程中出现错误，请重试。"
    
    async def _generate_chat_response(self) -> str:
        """使用 LLM 生成普通对话回复"""
        try:
            # 导入 LLM 客户端和提示词
            from yoloapp.llm import get_llm_client
            from yoloapp.prompt import CHAT_SYSTEM_PROMPT
            
            llm = get_llm_client()
            
            # 获取用户消息
            user_message = self.memory.get_last_user_message()
            if not user_message:
                return "抱歉，我没有收到您的消息。"
            
            # 调用 LLM
            messages = [
                Message.system_message(CHAT_SYSTEM_PROMPT),
                user_message
            ]
            
            response = await llm.ask(messages)
            
            logger.info(f"[{self.name}] LLM 生成回复: {len(response)} 字符")
            
            return response
            
        except Exception as e:
            logger.error(f"[{self.name}] LLM 生成失败: {e}")
            # 降级到简单回复
            return "收到您的消息。我是水稻病害智能助手，更擅长回答农业相关的问题。有什么可以帮您？"
    
    def _build_response(self) -> str:
        """构建最终响应"""
        # 导入响应模板
        from yoloapp.prompt import (
            GREETING_RESPONSE,
            GOODBYE_RESPONSE,
            CLARIFICATION_TEMPLATE,
            NO_IMAGE_RESPONSE,
        )
        
        parts = []
        
        # 0. 处理输入验证失败 - 澄清请求（优先级最高）
        input_validation = self.memory.metadata.get("input_validation", {})
        if input_validation.get("clarification_needed"):
            clarification_msg = input_validation.get("clarification_prompt", "请补充必要信息")
            return CLARIFICATION_TEMPLATE.format(message=clarification_msg)
        
        # 1. 处理问候和告别
        intent = self.memory.metadata.get("intent", "chat")
        if intent == "greet":
            return GREETING_RESPONSE
        
        if intent == "goodbye":
            return GOODBYE_RESPONSE
        
        # 2. 处理检测结果
        detection_result = self._get_detection_result()
        if detection_result:
            formatted_result = self._format_detection_result(detection_result)
            parts.append(f"🔬 {formatted_result}")
        
        # 3. 处理分析结果
        analysis_result = self._get_analysis_result()
        if analysis_result:
            formatted_analysis = self._format_analysis_result(analysis_result)
            if formatted_analysis:
                parts.append(formatted_analysis)
        
        # 4. 处理知识查询结果
        knowledge_result = self._get_knowledge_result()
        if knowledge_result and not detection_result:
            # 只有在没有检测结果时才添加知识结果，避免重复
            parts.append(knowledge_result)
        
        # 5. 组合最终响应
        if parts:
            return "\n\n".join(parts)
        
        # 默认响应
        if intent == "detect" and not self.memory.metadata.get("image_path"):
            return NO_IMAGE_RESPONSE
        
        return "收到您的问题。请问可以提供更多细节吗？"
    
    def _get_detection_result(self) -> str:
        """获取检测结果"""
        tool_results = self.memory.metadata.get("tool_results", [])
        for r in tool_results:
            if r.get("skill") == "DetectionSkill" and r.get("success"):
                result = r.get("result", "")
                if result and "检测到" in result:
                    return result
        return ""
    
    def _get_analysis_result(self) -> str:
        """获取分析结果"""
        tool_results = self.memory.metadata.get("tool_results", [])
        for r in tool_results:
            if r.get("skill") == "KnowledgeSkill" and r.get("action") == "analyze_detection":
                result = r.get("result", "")
                if result and "检测结果分析" in result:
                    return result
        return ""
    
    def _get_knowledge_result(self) -> str:
        """获取知识查询结果"""
        # 优先从 RAG 结果获取
        rag_results = self.memory.metadata.get("rag_results", [])
        logger.info(f"[{self.name}] RAG 结果数量: {len(rag_results)}")
        
        for i, r in enumerate(rag_results):
            logger.info(f"[{self.name}] RAG 结果 {i+1}: {len(r) if r else 0} 字符")
            if r and len(r) > 20:
                logger.info(f"[{self.name}] 使用 RAG 结果: {r[:100]}...")
                return r
        
        # 如果没有 RAG 结果，从 tool_results 获取
        tool_results = self.memory.metadata.get("tool_results", [])
        logger.info(f"[{self.name}] Tool 结果数量: {len(tool_results)}")
        
        for r in tool_results:
            if r.get("skill") == "KnowledgeSkill" and r.get("action") == "query_knowledge":
                result = r.get("result", "")
                logger.info(f"[{self.name}] KnowledgeSkill 结果: {len(result)} 字符")
                if result and len(result) > 20:
                    logger.info(f"[{self.name}] 使用 KnowledgeSkill 结果: {result[:100]}...")
                    return result
        
        logger.warning(f"[{self.name}] 未找到有效的知识结果")
        return ""
    
    def _format_detection_result(self, result: str) -> str:
        """格式化检测结果，转换英文为中文"""
        formatted = result
        
        # 替换病害名称
        for eng_name, cn_name in DISEASE_NAME_MAP.items():
            if eng_name in formatted:
                formatted = formatted.replace(eng_name, cn_name)
        
        # 移除置信度信息（简化输出）
        formatted = re.sub(r'\s*\(?置信度[：:]\s*[\d.]+%?\)?', '', formatted)
        formatted = re.sub(r'\s*\(置信度[：:]\s*[\d.]+\)', '', formatted)
        
        return formatted
    
    def _format_analysis_result(self, result: str) -> str:
        """格式化分析结果，提取有用信息"""
        lines = result.split('\n')
        useful_lines = []
        
        skip_keywords = [
            "检测结果分析", "用户问题", "未检测到任何对象",
            "请检查图片质量", "重新上传", "置信度"
        ]
        
        # 标记是否在有用部分
        in_useful_section = False
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if in_useful_section:
                    useful_lines.append("")
                continue
            
            # 跳过无用行
            if any(keyword in line_stripped for keyword in skip_keywords):
                in_useful_section = False
                continue
            
            # 检查是否进入有用部分
            if any(keyword in line_stripped for keyword in [
                "病害特征", "防治建议", "【病害", "【综合建议】"
            ]):
                in_useful_section = True
                useful_lines.append(line_stripped)
                continue
            
            # 如果在有用部分内，保留所有内容
            if in_useful_section:
                useful_lines.append(line_stripped)
                continue
            
            # 其他关键信息也保留
            if any(keyword in line_stripped for keyword in [
                "选用抗病", "种子消毒", "合理施肥",
                "发病初期", "注意事项", "病害名称"
            ]):
                useful_lines.append(line_stripped)
        
        return '\n'.join(useful_lines) if useful_lines else ""
    
    def _add_emotion(self, response: str) -> str:
        """添加情感处理"""
        emotion = self.memory.metadata.get("emotion", "neutral")
        
        if emotion == "negative":
            return "我理解您的心情。\n\n" + response
        elif emotion == "positive":
            return response + "\n\n😊 很高兴能帮到你！"
        elif emotion == "urgent":
            return "我马上帮您处理！\n\n" + response
        
        return response
