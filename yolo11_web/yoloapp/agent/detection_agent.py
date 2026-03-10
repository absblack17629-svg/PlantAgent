# -*- coding: utf-8 -*-
"""
检测 Agent

负责图像检测和病害识别。
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path

from yoloapp.agent.base import BaseAgent
from yoloapp.schema import AgentRole, Message
from yoloapp.exceptions import DetectionError, ModelLoadError, InferenceError
from yoloapp.utils.logger import get_logger

# 外部依赖
from services.detection_service import DetectionService  # 这个保留，因为它不在迁移范围内

logger = get_logger(__name__)


class DetectionAgent(BaseAgent):
    """检测 Agent
    
    专门负责图像检测任务，使用 YOLO 模型进行病害识别。
    
    Attributes:
        detection_service: 检测服务实例
        confidence_threshold: 置信度阈值
        current_image_path: 当前处理的图像路径
        detection_result: 检测结果
    """
    
    detection_service: Optional[DetectionService] = None
    confidence_threshold: float = 0.5
    current_image_path: Optional[str] = None
    detection_result: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        """初始化检测 Agent
        
        Args:
            **kwargs: 其他参数
        """
        # 设置默认值
        if "name" not in kwargs:
            kwargs["name"] = "detection_agent"
        if "role" not in kwargs:
            kwargs["role"] = AgentRole.DETECTION
        if "description" not in kwargs:
            kwargs["description"] = "负责图像检测和病害识别"
        
        super().__init__(**kwargs)
        
        # 初始化检测服务
        try:
            self.detection_service = DetectionService()
            if not self.detection_service.yolo_model:
                raise ModelLoadError(
                    model_path="YOLO model",
                    cause=Exception("模型未正确加载")
                )
            logger.info(f"检测 Agent {self.name} 初始化成功")
        except Exception as e:
            logger.error(f"检测 Agent {self.name} 初始化失败: {e}")
            raise
    
    async def step(self) -> str:
        """执行检测步骤
        
        Returns:
            步骤执行结果
            
        Raises:
            DetectionError: 如果检测失败
        """
        # 获取最后一条用户消息
        last_user_msg = self.memory.get_last_user_message()
        if not last_user_msg:
            self.mark_finished()
            return "没有待处理的请求"
        
        # 解析图像路径
        if not self.current_image_path:
            self.current_image_path = self._extract_image_path(last_user_msg.content)
            if not self.current_image_path:
                self.update_memory("assistant", "请提供图像路径")
                return "等待图像路径"
        
        # 执行检测
        try:
            logger.info(f"开始检测图像: {self.current_image_path}")
            
            # 在线程池中执行检测（YOLO 是 CPU 密集型）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._detect_sync,
                self.current_image_path
            )
            
            self.detection_result = result
            
            # 格式化结果
            result_text = self._format_detection_result(result)
            self.update_memory("assistant", result_text)
            
            # 标记完成
            self.mark_finished()
            
            logger.info(f"检测完成: {result}")
            return f"检测完成: {result_text}"
        
        except Exception as e:
            error_msg = f"检测失败: {str(e)}"
            logger.error(error_msg)
            self.update_memory("assistant", error_msg)
            raise InferenceError(
                image_path=self.current_image_path,
                cause=e
            )
    
    def _detect_sync(self, image_path: str) -> Dict[str, Any]:
        """同步检测方法
        
        Args:
            image_path: 图像路径
            
        Returns:
            检测结果字典
            
        Raises:
            InferenceError: 如果检测失败
        """
        try:
            # 检查文件是否存在
            if not Path(image_path).exists():
                raise FileNotFoundError(f"图像文件不存在: {image_path}")
            
            # 执行检测
            results = self.detection_service.yolo_model(
                image_path,
                conf=self.confidence_threshold
            )
            
            # 解析结果
            detections = []
            if results and len(results) > 0:
                result = results[0]
                if result.boxes:
                    for box in result.boxes:
                        detection = {
                            "class_id": int(box.cls[0]),
                            "class_name": result.names[int(box.cls[0])],
                            "confidence": float(box.conf[0]),
                            "bbox": box.xyxy[0].tolist()
                        }
                        detections.append(detection)
            
            return {
                "image_path": image_path,
                "detections": detections,
                "count": len(detections)
            }
        
        except Exception as e:
            logger.error(f"同步检测失败: {e}")
            raise
    
    def _extract_image_path(self, text: str) -> Optional[str]:
        """从文本中提取图像路径
        
        Args:
            text: 输入文本
            
        Returns:
            图像路径，如果未找到则返回 None
        """
        # 简单的路径提取逻辑
        # 可以根据实际需求改进
        import re
        
        # 匹配常见的图像路径模式
        patterns = [
            r'["\']([^"\']+\.(?:jpg|jpeg|png|bmp|gif))["\']',  # 引号包围的路径
            r'(\S+\.(?:jpg|jpeg|png|bmp|gif))',  # 不带引号的路径
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _format_detection_result(self, result: Dict[str, Any]) -> str:
        """格式化检测结果
        
        Args:
            result: 检测结果字典
            
        Returns:
            格式化的结果文本
        """
        if result["count"] == 0:
            return "未检测到任何病害"
        
        lines = [f"检测到 {result['count']} 个病害:"]
        for i, det in enumerate(result["detections"], 1):
            lines.append(
                f"{i}. {det['class_name']} "
                f"(置信度: {det['confidence']:.2%})"
            )
        
        return "\n".join(lines)
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """设置置信度阈值
        
        Args:
            threshold: 置信度阈值 (0-1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("置信度阈值必须在 0-1 之间")
        
        self.confidence_threshold = threshold
        logger.info(f"设置置信度阈值: {threshold}")
    
    def get_detection_result(self) -> Optional[Dict[str, Any]]:
        """获取检测结果
        
        Returns:
            检测结果字典，如果未检测则返回 None
        """
        return self.detection_result
    
    def reset(self) -> None:
        """重置 Agent"""
        super().reset()
        self.current_image_path = None
        self.detection_result = None
        logger.info(f"检测 Agent {self.name} 已重置")
