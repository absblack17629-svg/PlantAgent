# -*- coding: utf-8 -*-
"""
意图理解 Agent

节点 1：分析用户输入的意图和情感
"""

from typing import Optional, Dict, Any
from enum import Enum

from yoloapp.agent.base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import AgentError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class IntentType(str, Enum):
    """意图类型"""
    CHAT = "chat"
    DETECT = "detect"
    QUERY = "query"
    GREET = "greet"
    GOODBYE = "goodbye"


class EmotionType(str, Enum):
    """情感类型"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    URGENT = "urgent"


class IntentAgent(BaseAgent):
    """意图理解 Agent
    
    负责分析用户输入的意图和情感。
    
    Attributes:
        detected_intent: 检测到的意图
        detected_emotion: 检测到的情感
        confidence: 置信度
        image_path: 图像路径（如果有）
    """
    
    detected_intent: Optional[IntentType] = None
    detected_emotion: Optional[EmotionType] = None
    confidence: float = 0.0
    image_path: Optional[str] = None
    
    def __init__(self, **kwargs):
        """初始化意图理解 Agent"""
        if "name" not in kwargs:
            kwargs["name"] = "intent_agent"
        if "role" not in kwargs:
            kwargs["role"] = AgentRole.GENERAL
        if "description" not in kwargs:
            kwargs["description"] = "节点1：意图理解 + 情感分析"
        
        super().__init__(**kwargs)
        
        # 设置系统提示
        self.system_prompt = """你是一个意图理解专家。
分析用户输入，识别意图类型：
- greet: 问候
- goodbye: 告别
- detect: 图像检测请求
- query: 知识查询
- chat: 普通对话

同时分析情感：positive, neutral, negative, urgent"""
        
        logger.info(f"意图理解 Agent {self.name} 初始化成功")
    
    async def step(self) -> str:
        """执行意图理解步骤
        
        Returns:
            步骤执行结果
        """
        # 获取最后一条用户消息
        last_user_msg = self.memory.get_last_user_message()
        if not last_user_msg:
            self.mark_finished()
            return "没有待分析的输入"
        
        user_input = last_user_msg.content
        
        # 从元数据中获取图像路径
        self.image_path = last_user_msg.metadata.get("image_path")
        
        try:
            logger.info(f"开始意图分析: {user_input[:50]}...")
            
            # 分析意图
            intent, emotion, confidence = self._analyze_intent(user_input)
            
            self.detected_intent = intent
            self.detected_emotion = emotion
            self.confidence = confidence
            
            # 构建结果
            result = {
                "intent": intent.value,
                "emotion": emotion.value,
                "confidence": confidence
            }
            
            result_text = (
                f"意图: {intent.value}\n"
                f"情感: {emotion.value}\n"
                f"置信度: {confidence:.2%}"
            )
            
            # 保存到 Memory 的 metadata（重要！）
            self.memory.metadata["intent"] = intent.value
            self.memory.metadata["emotion"] = emotion.value
            self.memory.metadata["confidence"] = confidence
            
            # 记录到记忆
            self.update_memory(
                "assistant",
                result_text,
                metadata=result
            )
            
            # 标记完成
            self.mark_finished()
            
            logger.info(f"意图分析完成: {result}")
            return result_text
        
        except Exception as e:
            error_msg = f"意图分析失败: {str(e)}"
            logger.error(error_msg)
            self.update_memory("assistant", error_msg)
            raise AgentError(
                message=error_msg,
                error_code="INTENT_ANALYSIS_FAILED",
                context={"user_input": user_input}
            )
    
    def _analyze_intent(self, user_input: str) -> tuple:
        """分析意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            (意图, 情感, 置信度)
        """
        text = user_input.lower()
        
        # 先检查紧急情绪（优先级最高）
        urgent_keywords = ["紧急", "急", "快", "马上", "立即", "赶紧", "尽快"]
        is_urgent = any(w in text for w in urgent_keywords)
        
        # 问候检测
        if any(w in text for w in ["你好", "嗨", "hello", "hi", "您好"]):
            return IntentType.GREET, EmotionType.POSITIVE, 0.95
        
        # 告别检测
        if any(w in text for w in ["再见", "拜拜", "bye", "goodbye"]):
            return IntentType.GOODBYE, EmotionType.NEUTRAL, 0.95
        
        # 检测请求（扩展关键词列表）
        detect_keywords = [
            "检测", "识别", "分析图片", "这张图", "图片", "照片", 
            "看看", "帮我看", "帮我分析", "分析一下", "看一下",
            "帮忙看", "帮忙分析", "能帮我", "帮我检测", "帮我识别",
            "看下", "瞧瞧", "瞅瞅", "诊断", "判断"
        ]
        if any(w in text for w in detect_keywords) or self.image_path:
            emotion = EmotionType.URGENT if is_urgent else EmotionType.NEUTRAL
            return IntentType.DETECT, emotion, 0.9
        
        # 知识查询
        query_keywords = ["什么是", "怎么", "为什么", "如何", "介绍", "防治", "处理", "病", "症状", "原因", "出现"]
        if any(w in text for w in query_keywords):
            emotion = EmotionType.URGENT if is_urgent else EmotionType.NEUTRAL
            return IntentType.QUERY, emotion, 0.85
        
        # 默认为普通对话
        emotion = EmotionType.URGENT if is_urgent else EmotionType.NEUTRAL
        return IntentType.CHAT, emotion, 0.7
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """获取分析结果
        
        Returns:
            分析结果字典
        """
        if not self.detected_intent:
            return None
        
        return {
            "intent": self.detected_intent.value,
            "emotion": self.detected_emotion.value,
            "confidence": self.confidence,
            "image_path": self.image_path
        }
    
    def reset(self) -> None:
        """重置 Agent"""
        super().reset()
        self.detected_intent = None
        self.detected_emotion = None
        self.confidence = 0.0
        self.image_path = None
        logger.info(f"意图理解 Agent {self.name} 已重置")
