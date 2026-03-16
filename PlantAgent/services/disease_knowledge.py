# -*- coding: utf-8 -*-
"""
水稻病害知识库
基于RAG的水稻病害知识检索
"""

import json
from typing import List, Dict, Any, Optional

from services.rag_service import RAGService
from utils.logger import get_logger

logger = get_logger(__name__)


class DiseaseKnowledgeBase:
    """
    水稻病害知识库
    提供病害知识检索和问答支持
    """
    
    # 病害类型定义
    DISEASE_TYPES = {
        "白叶枯病": {
            "name": "水稻白叶枯病",
            "category": "细菌性病害",
            "symptoms": "叶片叶尖或叶缘产生黄绿色或暗绿色斑点，后沿叶脉扩展成条斑，病斑灰白色，病健部交界线明显，呈波纹状。湿度大时病斑上产生黄色菌脓。",
            "causes": "由黄单胞杆菌引起，病菌在种子和病草上越冬，借风雨、流水传播，从水孔或伤口侵入。高温多雨、洪涝淹水、偏施氮肥易发病。",
            "prevention": "选用抗病品种，健身栽培，科学管水，合理施肥。发病初期及时防治。",
            "medicine": "发病初期用20%噻菌铜悬浮剂600倍液，或50%氯溴异氰尿酸可溶粉剂1000倍液喷雾。",
            "period": "水稻分蘖至孕穗期",
            "varieties": "杂交稻、优质稻一般较耐病"
        },
        "稻瘟病": {
            "name": "水稻稻瘟病",
            "category": "真菌性病害",
            "symptoms": "根据部位不同可分为叶瘟、节瘟、穗颈瘟、谷粒瘟。叶瘟：梭形病斑，外黄褐色，中灰白色，有褐色坏死线。节瘟：节上产生褐色小点，后绕节扩展，使节部变黑褐色，易折断。穗颈瘟：穗颈上产生褐色小点，后扩展成黑褐色条斑，造成白穗。",
            "causes": "由稻瘟真菌引起，病菌以菌丝和分生孢子在病稻草和种子上越冬，借风雨传播。高湿、气温25-28℃时易发病。氮肥过多、过迟，低温寡照，连续阴雨易发病。",
            "prevention": "选用抗病品种，健身栽培，消灭菌源。发病时及时喷药防治。",
            "medicine": "发病初期用75%三环唑可湿性粉剂2000倍液，或40%稻瘟灵乳油800倍液，或咪鲜胺乳油1500倍液喷雾。",
            "period": "分蘖期、抽穗期易发病",
            "varieties": "粳稻、糯稻一般较籼稻抗病"
        },
        "褐斑病": {
            "name": "水稻褐斑病",
            "category": "真菌性病害",
            "symptoms": "叶片上产生褐色椭圆形病斑，大小约3-14×2-6mm，病斑中央灰褐色，边缘褐色，外围有黄色晕圈。病斑多时连成不规则大斑。",
            "causes": "由真菌引起，病菌在病叶和病残体上越冬，借风雨传播。高温多湿，多雨寡照，偏施氮肥易发病。",
            "prevention": "清除病残体，科学施肥，增施钾肥。发病初期喷药防治。",
            "medicine": "发病初期用50%多菌灵可湿性粉剂800倍液，或70%甲基硫菌灵可湿性粉剂1000倍液，或25%咪鲜胺乳油1500倍液喷雾。",
            "period": "水稻生长中后期",
            "varieties": "一般水稻品种均可感染"
        }
    }
    
    def __init__(self):
        self.rag_service = None
        self._initialized = False
    
    async def initialize(self):
        """初始化知识库"""
        if self._initialized:
            return
        
        # 初始化RAG服务
        try:
            self.rag_service = RAGService()
            await self.rag_service.init_async()
            logger.info("[OK] 病害知识库初始化完成")
        except Exception as e:
            logger.warning(f"[WARN] RAG服务初始化失败: {e}")
        
        self._initialized = True
    
    def get_disease_info(self, disease_type: str) -> Optional[Dict]:
        """
        获取病害详细信息
        
        Args:
            disease_type: 病害类型
            
        Returns:
            病害信息字典
        """
        return self.DISEASE_TYPES.get(disease_type)
    
    def get_all_diseases(self) -> List[Dict]:
        """
        获取所有病害类型列表
        
        Returns:
            病害列表
        """
        return [
            {
                "disease_type": disease_type,
                "name": info["name"],
                "category": info["category"]
            }
            for disease_type, info in self.DISEASE_TYPES.items()
        ]
    
    def get_prevention_scheme(self, disease_type: str) -> Optional[str]:
        """
        获取病害防治方案
        
        Args:
            disease_type: 病害类型
            
        Returns:
            防治方案文本
        """
        info = self.get_disease_info(disease_type)
        if not info:
            return None
        
        scheme = f"""
## {info['name']}防治方案

### 病害类型
{info['category']}

### 症状识别
{info['symptoms']}

### 发病原因
{info['causes']}

### 预防措施
{info['prevention']}

### 推荐用药
{info['medicine']}

### 易发时期
{info['period']}

### 易感品种
{info['varieties']}
"""
        return scheme.strip()
    
    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        检索病害知识
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        results = []
        
        # 1. 先从本地知识库检索
        for disease_type, info in self.DISEASE_TYPES.items():
            score = self._calculate_similarity(query, disease_type)
            if score > 0.3:
                results.append({
                    "disease_type": disease_type,
                    "content": self.get_prevention_scheme(disease_type),
                    "score": score,
                    "source": "knowledge_base"
                })
        
        # 2. 如果RAG可用，从向量库检索
        if self.rag_service:
            try:
                rag_results = await self.rag_service.search(query, top_k=top_k)
                results.extend(rag_results)
            except Exception as e:
                logger.warning(f"RAG检索失败: {e}")
        
        # 3. 按相似度排序
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return results[:top_k]
    
    def _calculate_similarity(self, query: str, disease_type: str) -> float:
        """
        计算简单相似度
        
        Args:
            query: 查询文本
            disease_type: 病害类型
            
        Returns:
            相似度分数
        """
        query_lower = query.lower()
        disease_lower = disease_type.lower()
        
        # 关键词匹配
        keywords = {
            "白叶枯病": ["白叶枯", "白叶", "细菌"],
            "稻瘟病": ["稻瘟", "瘟病", "穗颈瘟", "叶瘟"],
            "褐斑病": ["褐斑", "斑点", "褐"]
        }
        
        keyword_list = keywords.get(disease_type, [])
        matches = sum(1 for kw in keyword_list if kw in query_lower)
        
        if matches > 0:
            return 0.5 + matches * 0.15
        
        # 模糊匹配
        if disease_lower in query_lower:
            return 0.9
        
        # 任何关键词匹配
        for kw in keywords.values():
            if any(k in query_lower for k in kw):
                return 0.4
        
        return 0.0
    
    async def diagnose_by_symptom(self, symptom_description: str) -> List[Dict]:
        """
        根据症状诊断病害
        
        Args:
            symptom_description: 症状描述
            
        Returns:
            可能病害列表
        """
        diagnoses = []
        
        # 症状关键词映射
        symptom_keywords = {
            "白叶枯病": ["叶尖", "叶缘", "黄绿色", "条斑", "灰白色", "波纹", "菌脓"],
            "稻瘟病": ["梭形", "褐色", "白穗", "节瘟", "穗颈瘟", "坏死"],
            "褐斑病": ["椭圆形", "褐色", "斑点", "黄色晕圈"]
        }
        
        symptom_lower = symptom_description.lower()
        
        for disease_type, keywords in symptom_keywords.items():
            match_count = sum(1 for kw in keywords if kw in symptom_lower)
            if match_count > 0:
                confidence = min(match_count / len(keywords) * 2, 0.95)
                info = self.get_disease_info(disease_type)
                diagnoses.append({
                    "disease_type": disease_type,
                    "disease_name": info["name"],
                    "confidence": confidence,
                    "matched_symptoms": [kw for kw in keywords if kw in symptom_lower],
                    "prevention_scheme": self.get_prevention_scheme(disease_type)
                })
        
        # 按置信度排序
        diagnoses.sort(key=lambda x: x["confidence"], reverse=True)
        
        return diagnoses


# 全局实例
_disease_knowledge = None


def get_disease_knowledge() -> DiseaseKnowledgeBase:
    """获取病害知识库单例"""
    global _disease_knowledge
    if _disease_knowledge is None:
        _disease_knowledge = DiseaseKnowledgeBase()
    return _disease_knowledge
