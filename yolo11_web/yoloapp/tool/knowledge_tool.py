# -*- coding: utf-8 -*-
"""
知识工具

提供知识库查询和检测结果分析功能。
"""

import re
from typing import Dict, Any, List, Tuple, Optional

from .base import BaseTool, ToolResult
from yoloapp.exceptions import RAGError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class KnowledgeTool(BaseTool):
    """知识库查询工具
    
    提供农业知识库查询功能，支持 RAG 检索和硬编码知识降级。
    
    Attributes:
        rag_service: RAG 服务实例
        llm: LLM 实例
    """
    
    name: str = "query_knowledge"
    description: str = "查询农业知识库，获取水稻病害、种植技术等相关知识"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "查询问题"
            }
        },
        "required": ["question"]
    }
    
    rag_service: Any = None
    llm: Any = None
    _rag_initialized: bool = False
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化知识工具"""
        super().__init__(**data)
        logger.info(f"初始化知识工具: {self.name}")
    
    async def initialize_rag(self, rag_service=None, llm=None):
        """初始化 RAG 服务
        
        Args:
            rag_service: RAG 服务实例
            llm: LLM 实例
        """
        if self._rag_initialized:
            return
        
        try:
            if rag_service:
                self.rag_service = rag_service
                self.llm = llm
                await self.rag_service.init_async()
                self._rag_initialized = True
                logger.info("RAG 服务已初始化")
        except Exception as e:
            logger.warning(f"RAG 初始化失败: {e}")
            self.rag_service = None
            self.llm = None
    
    async def execute(self, question: str, **kwargs) -> ToolResult:
        """查询知识库
        
        Args:
            question: 查询问题
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 查询结果
        """
        question_lower = question.lower()
        logger.info(f"查询知识库: {question}")
        
        # 1. 识别超出范围的问题
        out_of_scope_keywords = ["天气", "气温", "降雨", "预报", "温度", "下雨", "晴天", "阴天"]
        if any(keyword in question_lower for keyword in out_of_scope_keywords):
            response = """抱歉，我是水稻病害智能助手，主要专注于：
- 🌾 水稻病害识别与防治
- 🔬 农作物病害诊断
- [WATER] 农业灌溉管理
- 🌱 水稻种植技术

天气预测不在我的专业范围内。建议您：
- 查看天气预报应用或网站
- 咨询当地气象部门

如果您有水稻种植或病害防治方面的问题，我很乐意帮助！"""
            
            return self.success_response(
                data={"answer": response, "source": "out_of_scope"},
                message="问题超出范围"
            )
        
        # 2. 尝试使用 RAG 检索
        if self.rag_service and self.llm:
            try:
                logger.info("使用 RAG 检索知识")
                rag_response = await self.rag_service.query_knowledge_base(question, self.llm)
                
                if rag_response and len(rag_response) > 50:
                    logger.info(f"RAG 返回结果: {len(rag_response)} 字符")
                    response = f"📚 知识库检索结果：\n\n{rag_response}"
                    
                    return self.success_response(
                        data={"answer": response, "source": "rag"},
                        message="RAG 检索成功"
                    )
                else:
                    logger.warning("RAG 返回内容太短，使用降级方案")
            
            except Exception as e:
                logger.warning(f"RAG 检索失败: {e}，使用降级方案")
        else:
            logger.info("RAG 服务未初始化，使用硬编码知识")
        
        # 3. 降级方案：硬编码知识
        response = self._get_hardcoded_knowledge(question_lower)
        
        return self.success_response(
            data={"answer": response, "source": "hardcoded"},
            message="使用硬编码知识"
        )
    
    def _get_hardcoded_knowledge(self, question_lower: str) -> str:
        """获取硬编码知识
        
        Args:
            question_lower: 小写的问题文本
            
        Returns:
            知识内容
        """
        # 水稻相关问题
        if "水稻" in question_lower or "稻" in question_lower:
            return """📚 水稻种植与病害防治知识：

【常见水稻病害】

1. 稻瘟病：
   - 症状：叶片上出现褐色病斑，严重时形成白穗
   - 防治：选用抗病品种、合理施肥、适时灌溉、喷洒杀菌剂

2. 纹枯病：
   - 症状：茎秆基部出现褐色条斑，逐渐向上蔓延
   - 防治：改善通风、合理密植、适量施肥、喷洒药剂防治

3. 白叶枯病：
   - 症状：叶片出现黄白色条斑，病健交界明显
   - 防治：选用抗病品种、种子消毒、轮作、喷洒抗生素

4. 细菌性条斑病：
   - 症状：叶片上出现黄绿色条斑
   - 防治：选用抗病品种、做好种子消毒、喷洒噻霉酮

建议咨询当地农业专家获取更具体的防治方案。"""
        
        # 病害相关问题
        elif "病害" in question_lower or "病" in question_lower:
            return """📚 农作物病害防治知识：

【病害类型】

1. 真菌性病害：
   - 特点：高温高湿条件下易发病
   - 常见：稻瘟病、纹枯病、褐斑病
   - 防治：使用杀菌剂、改善通风、合理施肥

2. 细菌性病害：
   - 特点：通过伤口或昆虫传播
   - 常见：白叶枯病、细菌性条斑病
   - 防治：选用抗病品种、种子消毒、轮作

【综合防治原则】
- 预防为主，综合防治
- 选用抗病品种
- 加强田间管理
- 科学用药，交替使用不同药剂

具体防治方法需要根据作物类型和当地气候条件确定。"""
        
        # 灌溉管理问题
        elif "灌溉" in question_lower or "浇水" in question_lower or "水分" in question_lower:
            return """📚 农业灌溉管理知识：

【水稻灌溉原则】

1. 分蘖期：
   - 浅水勤灌，保持3-5cm水层
   - 促进分蘖，增加有效穗数

2. 拔节孕穗期：
   - 保持5-7cm水层
   - 满足水稻需水高峰期

3. 抽穗开花期：
   - 保持浅水层2-3cm
   - 防止高温影响授粉

4. 灌浆成熟期：
   - 干湿交替，间歇灌溉
   - 收获前7-10天断水

【节水灌溉技术】
- 间歇灌溉：节水20-30%
- 控制灌溉：根据土壤湿度调节
- 雨水收集利用

【注意事项】
- 避免长期深水淹灌
- 注意排水防涝
- 结合天气情况调整灌溉"""
        
        # 施肥问题
        elif "肥料" in question_lower or "施肥" in question_lower or "营养" in question_lower:
            return """📚 水稻施肥技术：

【施肥原则】
- 基肥为主，追肥为辅
- 有机肥与化肥结合
- 氮磷钾配合施用

【施肥时期】

1. 基肥（插秧前）：
   - 有机肥 + 复合肥
   - 占总施肥量的60-70%

2. 分蘖肥（插秧后7-10天）：
   - 速效氮肥
   - 促进分蘖

3. 穗肥（拔节期）：
   - 氮钾肥配合
   - 促进穗分化

4. 粒肥（抽穗后）：
   - 少量氮肥
   - 防止早衰

【注意事项】
- 避免偏施氮肥
- 增施钾肥提高抗病性
- 根据土壤肥力调整用量"""
        
        # 通用农业问题
        else:
            return """📚 农业知识查询：

我是水稻病害智能助手，可以为您提供以下方面的专业知识：

🌾 水稻种植技术
   - 育苗、插秧、田间管理
   - 生长期管理要点

🔬 农作物病害防治
   - 病害识别与诊断
   - 综合防治方案

[WATER] 农业灌溉管理
   - 灌溉时期与方法
   - 节水灌溉技术

🌱 肥料施用技术
   - 施肥时期与用量
   - 配方施肥建议

请告诉我您具体想了解哪方面的内容，我会为您提供详细的专业建议。"""


class DetectionAnalysisTool(BaseTool):
    """检测结果分析工具
    
    分析检测结果并提供病害防治建议。
    """
    
    name: str = "analyze_detection"
    description: str = "分析检测结果，提供病害识别和防治建议"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "用户问题"
            },
            "detections": {
                "type": "string",
                "description": "检测结果文本"
            }
        },
        "required": ["question", "detections"]
    }
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化分析工具"""
        super().__init__(**data)
        logger.info(f"初始化分析工具: {self.name}")
    
    async def execute(self, question: str, detections: str, **kwargs) -> ToolResult:
        """分析检测结果
        
        Args:
            question: 用户问题
            detections: 检测结果
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 分析结果
        """
        try:
            logger.info(f"分析检测结果: question={question[:50]}...")
            logger.debug(f"检测结果: {detections[:100]}")
            
            # 病害名称映射
            disease_map = {
                "Bacterialblight": "细菌性条斑病",
                "Browspot": "褐斑病",
                "Blast": "稻瘟病",
                "Leafblast": "叶瘟",
                "Neckblast": "穗颈瘟",
                "Sheathblight": "纹枯病",
                "Ricehispa": "稻负泥虫",
                "Tungro": "东格鲁病",
                "Yellow": "黄化病",
                "False": "假病斑"
            }
            
            analysis_result = f"检测结果分析：\n\n用户问题：{question}\n\n"
            
            # 精确提取病害名称和置信度
            detected_diseases = self._extract_diseases_precise(detections, disease_map)
            
            logger.info(f"精确提取到: {len(detected_diseases)} 个病害")
            
            if detected_diseases:
                analysis_result += f"[OK] 检测到 {len(detected_diseases)} 种病害\n\n"
                
                # 对每个检测到的病害进行详细分析
                for i, (eng_name, cn_name, confidence) in enumerate(detected_diseases, 1):
                    analysis_result += f"【病害 {i}】\n"
                    analysis_result += f"病害名称：{cn_name}\n"
                    
                    # 添加详细描述和防治建议
                    if eng_name == "Bacterialblight":
                        analysis_result += self._get_bacterialblight_info()
                    elif eng_name == "Browspot":
                        analysis_result += self._get_browspot_info()
                    elif eng_name == "Blast":
                        analysis_result += self._get_blast_info()
                    else:
                        analysis_result += self._get_generic_disease_info(cn_name, eng_name)
                    
                    analysis_result += "\n"
                
                # 添加总体建议
                analysis_result += "【综合建议】\n"
                analysis_result += "1. 根据检测到的病害采取相应防治措施\n"
                analysis_result += "2. 建议咨询当地农业技术人员获取针对性方案\n"
                analysis_result += "3. 注意观察病情发展，及时调整防治策略\n"
                
                return self.success_response(
                    data={
                        "analysis": analysis_result,
                        "diseases": detected_diseases,
                        "count": len(detected_diseases)
                    },
                    message="分析完成"
                )
            
            else:
                analysis_result += "[FAIL] 未检测到明确病害\n"
                analysis_result += "\n可能原因：\n"
                analysis_result += "1. 图片中无明显病害特征\n"
                analysis_result += "2. 检测模型可能未训练此类病害\n"
                analysis_result += "3. 图片质量或光线不佳\n"
                analysis_result += "\n建议：\n"
                analysis_result += "- 重新拍摄更清晰的图片\n"
                analysis_result += "- 确保病斑区域完整显示在图片中\n"
                
                return self.success_response(
                    data={
                        "analysis": analysis_result,
                        "diseases": [],
                        "count": 0
                    },
                    message="未检测到病害"
                )
        
        except Exception as e:
            logger.error(f"分析失败: {e}", exc_info=True)
            return self.fail_response(
                error=f"分析失败: {str(e)}",
                error_code="ANALYSIS_FAILED"
            )
    
    def _extract_diseases_precise(
        self,
        detections: str,
        disease_map: Dict[str, str]
    ) -> List[Tuple[str, str, float]]:
        """精确提取病害信息
        
        Args:
            detections: 检测结果文本
            disease_map: 病害名称映射
            
        Returns:
            病害列表 [(英文名, 中文名, 置信度), ...]
        """
        detected = []
        detected_names = set()
        
        # 模式1: 逐行匹配 "1. 细菌性条斑病 (置信度: 0.88)"
        pattern1 = r'(\d+)\.\s*([^\(]+)\s*\(置信度[：:]\s*([\d.]+)\)'
        matches = list(re.finditer(pattern1, detections))
        
        if matches:
            logger.debug(f"模式1匹配到 {len(matches)} 个结果")
            for match in matches:
                disease_text = match.group(2).strip()
                confidence = match.group(3)
                
                # 尝试匹配病害名称
                disease_name = None
                for eng_name, cn_name in disease_map.items():
                    if eng_name in disease_text or cn_name in disease_text:
                        disease_name = (eng_name, cn_name)
                        break
                
                if disease_name and disease_name[0] not in detected_names:
                    detected.append((disease_name[0], disease_name[1], float(confidence)))
                    detected_names.add(disease_name[0])
                    logger.debug(f"识别病害: {disease_name[1]} - 置信度: {confidence}")
        
        # 模式2: 直接查找病害名称（无置信度）
        if not detected:
            for eng_name, cn_name in disease_map.items():
                if eng_name in detections or cn_name in detections:
                    detected.append((eng_name, cn_name, 0.0))
                    logger.debug(f"模式2识别病害: {cn_name} - 无置信度")
                    break
        
        return detected
    
    def _get_bacterialblight_info(self) -> str:
        """细菌性条斑病详细信息"""
        return """病害特征：
- 细菌性条斑病是水稻的重要细菌性病害
- 主要症状是叶片出现黄褐色条斑，后期呈灰白色
- 病斑上常有菌脓，干燥后呈菌痂
- 严重时会导致叶片枯死，影响产量

防治建议：
1. 选用抗病品种，从源头预防
2. 种子消毒，用温汤浸种或农用链霉素浸种
3. 合理施肥，避免偏施氮肥，增强植株抗病能力
4. 及时排水，避免田间积水，减少细菌传播
5. 发病初期喷洒农用链霉素、叶枯唑或噻霉酮等药剂
6. 实行轮作，减少病原菌积累"""
    
    def _get_browspot_info(self) -> str:
        """褐斑病详细信息"""
        return """病害特征：
- 褐斑病是水稻常见的真菌性病害
- 主要危害叶片，形成褐色小斑点
- 病斑边缘不规则，中央呈灰白色
- 严重时病斑密布，叶片枯黄

防治建议：
1. 清除病残体，减少初侵染源
2. 合理密植，改善通风透光条件
3. 避免偏施氮肥，增施磷钾肥
4. 发病初期喷洒多菌灵、甲基托布津等杀菌剂
5. 注意田间排水，降低湿度"""
    
    def _get_blast_info(self) -> str:
        """稻瘟病详细信息"""
        return """病害特征：
- 稻瘟病是水稻最严重的病害之一
- 可危害叶片、茎秆和穗部
- 叶片病斑呈梭形，边缘褐色，中央灰白色
- 穗颈瘟会导致白穗，造成严重减产

防治建议：
1. 选用抗病品种是最有效的方法
2. 合理施肥，避免偏施氮肥
3. 适时灌溉，避免长期深水
4. 发病初期喷洒三环唑、稻瘟灵、富士一号等
5. 清除病残体，减少菌源"""
    
    def _get_generic_disease_info(self, cn_name: str, eng_name: str) -> str:
        """通用病害信息"""
        return f"""病害特征：
- {cn_name}（{eng_name}）是检测到的病害

防治建议：
1. 及时采取防治措施
2. 咨询当地农业技术人员获取针对性建议
3. 参考相关病害防治资料"""


# 工厂函数
def get_knowledge_tool() -> KnowledgeTool:
    """获取知识工具实例"""
    return KnowledgeTool()


def get_detection_analysis_tool() -> DetectionAnalysisTool:
    """获取检测分析工具实例"""
    return DetectionAnalysisTool()
