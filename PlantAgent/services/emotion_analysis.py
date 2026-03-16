# -*- coding: utf-8 -*-
"""
情感分析模块
水稻病害识别系统的情感感知组件
"""

import re
from typing import Dict, Tuple
from enum import Enum

import config
from utils.logger import get_logger

logger = get_logger(__name__)


class SentimentType(Enum):
    """情感类型"""
    POSITIVE = "positive"     # 积极
    NEUTRAL = "neutral"       # 中性
    NEGATIVE = "negative"     # 负面
    URGENT = "urgent"         # 紧急


class EmotionAnalyzer:
    """
    情感分析器
    支持关键词+规则的情感识别
    """
    
    # 负面情感关键词
    NEGATIVE_KEYWORDS = [
        "担心", "害怕", "焦虑", "着急", "慌", "怎么办", "完了",
        "死了", "严重", "糟糕", "坏了", "损失", "心疼", "难过",
        "伤心", "绝望", "无助", "无奈", "烦", "愁", "怕",
        "求救", "救命", "紧急", "危重"
    ]
    
    # 紧急情感关键词
    URGENT_KEYWORDS = [
        "紧急", "危急", "危重", "快要死了", "马上", "立即",
        "赶紧", "来不及了", "救命", "求救", "急救", "急性",
        "爆发", "大面积", "传染", "控制不住"
    ]
    
    # 积极情感关键词
    POSITIVE_KEYWORDS = [
        "谢谢", "感谢", "太好了", "很好", "不错", "棒", "优秀",
        "完美", "满意", "高兴", "开心", "喜欢", "有用", "帮大忙"
    ]
    
    # 负面情感模式
    NEGATIVE_PATTERNS = [
        r"(.+?)怎么办",
        r"(.+?)救",
        r"(.+?)完了",
        r"损失(.+?)",
        r"死(.+?)",
        r"全完了",
    ]
    
    # 紧急情感模式
    URGENT_PATTERNS = [
        r"紧急",
        r"危急",
        r"危重",
        r"马上",
        r"立即",
        r"来不及",
        r"救命",
        r"急救",
    ]
    
    def __init__(self):
        self.enabled = config.settings.ENABLE_SENTIMENT_ANALYSIS
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        self.negative_patterns = [re.compile(p, re.IGNORECASE) for p in self.NEGATIVE_PATTERNS]
        self.urgent_patterns = [re.compile(p, re.IGNORECASE) for p in self.URGENT_PATTERNS]
    
    def analyze(self, text: str) -> Tuple[SentimentType, float]:
        """
        分析文本情感
        
        Args:
            text: 待分析文本
            
        Returns:
            (情感类型, 置信度)
        """
        if not self.enabled:
            return SentimentType.NEUTRAL, 0.0
        
        if not text:
            return SentimentType.NEUTRAL, 0.0
        
        text_lower = text.lower()
        scores = {
            SentimentType.POSITIVE: 0.0,
            SentimentType.NEUTRAL: 0.3,
            SentimentType.NEGATIVE: 0.0,
            SentimentType.URGENT: 0.0
        }
        
        # 检查紧急关键词
        for keyword in self.URGENT_KEYWORDS:
            if keyword in text_lower:
                scores[SentimentType.URGENT] += 0.8
        
        # 检查紧急模式
        for pattern in self.urgent_patterns:
            if pattern.search(text):
                scores[SentimentType.URGENT] += 0.5
        
        # 检查负面关键词
        for keyword in self.NEGATIVE_KEYWORDS:
            if keyword in text_lower:
                scores[SentimentType.NEGATIVE] += 0.5
        
        # 检查负面模式
        for pattern in self.negative_patterns:
            if pattern.search(text):
                scores[SentimentType.NEGATIVE] += 0.4
        
        # 检查积极关键词
        for keyword in self.POSITIVE_KEYWORDS:
            if keyword in text_lower:
                scores[SentimentType.POSITIVE] += 0.6
        
        # 归一化置信度
        total = sum(scores.values())
        if total > 0:
            for sentiment in scores:
                scores[sentiment] /= total
        
        # 紧急情感优先
        if scores[SentimentType.URGENT] >= 0.3:
            return SentimentType.URGENT, min(scores[SentimentType.URGENT], 1.0)
        
        # 找最高分
        max_sentiment = SentimentType.NEUTRAL
        max_score = scores[SentimentType.NEUTRAL]
        
        for sentiment, score in scores.items():
            if score > max_score:
                max_score = score
                max_sentiment = sentiment
        
        confidence = max_score
        if confidence < 0.2:
            max_sentiment = SentimentType.NEUTRAL
            confidence = 0.5
        
        logger.debug(f"情感分析结果: {max_sentiment.value}, 置信度: {confidence:.2f}")
        
        return max_sentiment, confidence
    
    def get_comfort_response(self, sentiment: SentimentType) -> str:
        """
        获取安慰性回复
        
        Args:
            sentiment: 情感类型
            
        Returns:
            安慰性回复文本
        """
        comfort_responses = {
            SentimentType.URGENT: [
                "我理解您很着急，我马上帮您处理！",
                "请您别慌，我立即为您分析情况！",
                "收到！我会尽快为您解决问题。"
            ],
            SentimentType.NEGATIVE: [
                "我理解您的心情，让我们一起想办法解决。",
                "别担心，我会尽力帮助您。",
                "请您放心，我们会找到解决办法的。"
            ],
            SentimentType.POSITIVE: [
                "很高兴能帮到您！",
                "不客气，这是我们应该做的！"
            ],
            SentimentType.NEUTRAL: []
        }
        
        responses = comfort_responses.get(sentiment, [])
        if responses:
            import random
            return random.choice(responses)
        return ""
    
    def should_add_comfort(self, sentiment: SentimentType, confidence: float) -> bool:
        """
        判断是否需要添加安慰性表述
        
        Args:
            sentiment: 情感类型
            confidence: 置信度
            
        Returns:
            是否需要添加
        """
        if sentiment in [SentimentType.URGENT, SentimentType.NEGATIVE]:
            return confidence >= 0.3
        return False


# 全局实例
_emotion_analyzer = None


def get_emotion_analyzer() -> EmotionAnalyzer:
    """获取情感分析器单例"""
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer


def analyze_sentiment(text: str) -> Tuple[SentimentType, float]:
    """
    分析文本情感的便捷函数
    """
    analyzer = get_emotion_analyzer()
    return analyzer.analyze(text)
