# -*- coding: utf-8 -*-
"""
检测流程

编排检测和知识 Agent，完成图像检测和建议生成。
"""

from typing import Dict, Any, Optional
from pathlib import Path

from yoloapp.flow.base import BaseFlow
from yoloapp.agent.detection_agent import DetectionAgent
from yoloapp.agent.knowledge_agent import KnowledgeAgent
from yoloapp.exceptions import FlowError, AgentNotFoundError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class DetectionFlow(BaseFlow):
    """检测流程
    
    完整的检测流程包括：
    1. 图像检测（DetectionAgent）
    2. 知识查询（KnowledgeAgent）
    3. 结果整合
    
    Attributes:
        auto_query_knowledge: 是否自动查询知识
        confidence_threshold: 检测置信度阈值
    """
    
    auto_query_knowledge: bool = True
    confidence_threshold: float = 0.5
    
    def __init__(self, **kwargs):
        """初始化检测流程
        
        Args:
            **kwargs: 其他参数
        """
        if "name" not in kwargs:
            kwargs["name"] = "detection_flow"
        if "description" not in kwargs:
            kwargs["description"] = "图像检测和建议生成流程"
        
        super().__init__(**kwargs)
        
        # 创建并添加 Agent
        self._setup_agents()
        
        logger.info(f"检测流程 {self.name} 初始化成功")
    
    def _setup_agents(self) -> None:
        """设置 Agent"""
        try:
            # 创建检测 Agent
            detection_agent = DetectionAgent(
                confidence_threshold=self.confidence_threshold
            )
            self.add_agent("detection", detection_agent)
            
            # 创建知识 Agent
            knowledge_agent = KnowledgeAgent()
            self.add_agent("knowledge", knowledge_agent)
            
            # 设置主 Agent 为检测 Agent
            self.set_primary_agent("detection")
            
            logger.info("检测流程 Agent 设置完成")
        
        except Exception as e:
            logger.error(f"设置 Agent 失败: {e}")
            raise FlowError(
                message=f"检测流程初始化失败: {str(e)}",
                error_code="FLOW_SETUP_FAILED",
                context={"error": str(e)}
            )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行检测流程
        
        Args:
            input_data: 输入数据，包含：
                - image_path: 图像路径（必需）
                - user_query: 用户查询（可选）
                - auto_query: 是否自动查询知识（可选）
                
        Returns:
            执行结果字典，包含：
                - detection: 检测结果
                - knowledge: 知识查询结果（如果有）
                - summary: 结果摘要
                
        Raises:
            FlowError: 流程执行失败
        """
        # 验证输入
        image_path = input_data.get("image_path")
        if not image_path:
            raise FlowError(
                message="缺少必需参数: image_path",
                error_code="MISSING_IMAGE_PATH",
                context=input_data
            )
        
        # 检查文件是否存在
        if not Path(image_path).exists():
            raise FlowError(
                message=f"图像文件不存在: {image_path}",
                error_code="IMAGE_NOT_FOUND",
                context={"image_path": image_path}
            )
        
        user_query = input_data.get("user_query", f"请检测这张图片: {image_path}")
        auto_query = input_data.get("auto_query", self.auto_query_knowledge)
        
        result = {
            "detection": None,
            "knowledge": None,
            "summary": ""
        }
        
        try:
            # 步骤 1: 执行图像检测
            logger.info(f"步骤 1: 执行图像检测 - {image_path}")
            detection_agent = self.require_agent("detection")
            
            # 设置图像路径
            detection_agent.current_image_path = image_path
            
            # 执行检测
            detection_summary = await detection_agent.run(user_query)
            detection_result = detection_agent.get_detection_result()
            
            result["detection"] = detection_result
            logger.info(f"检测完成: {detection_result}")
            
            # 步骤 2: 根据检测结果查询知识（如果需要）
            if auto_query and detection_result and detection_result.get("count", 0) > 0:
                logger.info("步骤 2: 查询相关知识")
                knowledge_agent = self.require_agent("knowledge")
                
                # 构建知识查询
                knowledge_query = self._build_knowledge_query(detection_result)
                
                # 执行知识查询
                knowledge_summary = await knowledge_agent.run(knowledge_query)
                knowledge_result = knowledge_agent.get_knowledge_result()
                
                result["knowledge"] = knowledge_result
                logger.info(f"知识查询完成: {knowledge_result}")
            else:
                logger.info("步骤 2: 跳过知识查询")
                result["knowledge"] = {"message": "未执行知识查询"}
            
            # 步骤 3: 生成摘要
            result["summary"] = self._generate_summary(result)
            
            logger.info("检测流程执行完成")
            return result
        
        except Exception as e:
            error_msg = f"检测流程执行失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise FlowError(
                message=error_msg,
                error_code="DETECTION_FLOW_FAILED",
                context={
                    "image_path": image_path,
                    "error": str(e),
                    "partial_result": result
                }
            )
    
    def _build_knowledge_query(self, detection_result: Dict[str, Any]) -> str:
        """构建知识查询
        
        Args:
            detection_result: 检测结果
            
        Returns:
            知识查询文本
        """
        detections = detection_result.get("detections", [])
        if not detections:
            return "水稻病害防治建议"
        
        # 提取病害名称
        disease_names = [det["class_name"] for det in detections]
        unique_diseases = list(set(disease_names))
        
        if len(unique_diseases) == 1:
            return f"{unique_diseases[0]}的症状、原因和防治方法"
        else:
            diseases_str = "、".join(unique_diseases)
            return f"{diseases_str}的症状、原因和防治方法"
    
    def _generate_summary(self, result: Dict[str, Any]) -> str:
        """生成结果摘要
        
        Args:
            result: 执行结果
            
        Returns:
            摘要文本
        """
        lines = []
        
        # 检测结果摘要
        detection = result.get("detection")
        if detection:
            count = detection.get("count", 0)
            if count == 0:
                lines.append("[OK] 未检测到病害")
            else:
                lines.append(f"🔬 检测到 {count} 个病害:")
                for i, det in enumerate(detection.get("detections", [])[:3], 1):
                    lines.append(
                        f"  {i}. {det['class_name']} "
                        f"(置信度: {det['confidence']:.2%})"
                    )
        
        # 知识查询摘要
        knowledge = result.get("knowledge")
        if knowledge and knowledge.get("count", 0) > 0:
            lines.append(f"\n📚 找到 {knowledge['count']} 条相关知识")
        
        return "\n".join(lines) if lines else "执行完成"
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """设置检测置信度阈值
        
        Args:
            threshold: 置信度阈值 (0-1)
        """
        self.confidence_threshold = threshold
        
        # 更新检测 Agent 的阈值
        detection_agent = self.get_agent("detection")
        if detection_agent:
            detection_agent.set_confidence_threshold(threshold)
        
        logger.info(f"设置检测置信度阈值: {threshold}")
    
    def set_auto_query_knowledge(self, auto_query: bool) -> None:
        """设置是否自动查询知识
        
        Args:
            auto_query: 是否自动查询
        """
        self.auto_query_knowledge = auto_query
        logger.info(f"设置自动查询知识: {auto_query}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"DetectionFlow(agents={len(self.agents)}, auto_query={self.auto_query_knowledge})"


# 工厂函数
def create_detection_flow(
    confidence_threshold: float = 0.5,
    auto_query_knowledge: bool = True
) -> DetectionFlow:
    """创建检测流程实例
    
    Args:
        confidence_threshold: 检测置信度阈值
        auto_query_knowledge: 是否自动查询知识
        
    Returns:
        DetectionFlow 实例
    """
    return DetectionFlow(
        confidence_threshold=confidence_threshold,
        auto_query_knowledge=auto_query_knowledge
    )
