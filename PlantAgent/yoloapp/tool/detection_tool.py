# -*- coding: utf-8 -*-
"""
检测工具

提供图片目标检测和缓存管理功能。
"""

import os
from typing import Dict, Any

from .base import BaseTool, ToolResult
from yoloapp.exceptions import DetectionError
from yoloapp.utils.logger import get_logger

# 外部依赖（这些服务不在迁移范围内，保留原路径）
from services.detection_service import DetectionService
from services.cache_service import get_cache_service

logger = get_logger(__name__)


class DetectionTool(BaseTool):
    """目标检测工具
    
    提供图片目标检测功能，支持结果缓存。
    
    Attributes:
        detection_service: 检测服务实例
        cache_service: 缓存服务实例
    """
    
    # 工具定义
    name: str = "detect_objects"
    description: str = "对图片进行目标检测，识别其中的对象并返回检测结果"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "要检测的图片文件路径"
            }
        },
        "required": ["image_path"]
    }
    
    # 服务实例（使用 Field 避免 Pydantic 验证）
    detection_service: Any = None
    cache_service: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化检测工具"""
        super().__init__(**data)
        
        # 初始化服务
        if self.detection_service is None:
            self.detection_service = DetectionService()
        
        if self.cache_service is None:
            self.cache_service = get_cache_service()
        
        logger.info(f"初始化检测工具: {self.name}")
    
    async def execute(self, image_path: str, **kwargs) -> ToolResult:
        """执行目标检测
        
        Args:
            image_path: 图片文件路径
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 检测结果
            
        Raises:
            DetectionError: 检测失败
        """
        # 规范化路径
        image_path = os.path.normpath(image_path)
        logger.info(f"开始检测图片: {image_path}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return self.fail_response(
                error=f"图片文件不存在: {image_path}",
                error_code="FILE_NOT_FOUND",
                image_path=image_path
            )
        
        try:
            # 1. 尝试从缓存获取结果
            cached_result = self.cache_service.get('detection', image_path)
            if cached_result:
                logger.info(f"使用缓存的检测结果: {image_path}")
                return self.success_response(
                    data=cached_result,
                    message="使用缓存结果",
                    cached=True,
                    image_path=image_path
                )
            
            # 2. 缓存未命中，执行检测
            logger.info(f"执行新的检测: {image_path}")
            results = await self.detection_service.detect_objects(image_path)
            
            # 3. 格式化结果
            if not results:
                response_text = "未检测到任何对象"
                detection_data = {
                    "count": 0,
                    "objects": [],
                    "message": response_text
                }
            else:
                detection_summary = []
                objects_list = []
                
                for i, detection in enumerate(results, 1):
                    category = detection.get('类别', '未知')
                    confidence = detection.get('置信度', 0)
                    
                    objects_list.append({
                        "index": i,
                        "category": category,
                        "confidence": confidence
                    })
                    
                    detection_summary.append(f"{category}(置信度{confidence:.2f})")
                
                response_text = f"检测到 {len(results)} 个对象：\n"
                for obj in objects_list:
                    response_text += f"{obj['index']}. {obj['category']} (置信度: {obj['confidence']:.2f})\n"
                
                detection_data = {
                    "count": len(results),
                    "objects": objects_list,
                    "summary": detection_summary,
                    "message": response_text
                }
                
                # 4. 自动保存检测结果到记忆（可选）
                try:
                    from yoloapp.tool.memory_tool import get_memory_tool
                    memory_tool = get_memory_tool()
                    if memory_tool:
                        memory_context = f"图片检测结果：检测到{len(results)}个对象，包括：{', '.join(detection_summary[:5])}"
                        if len(detection_summary) > 5:
                            memory_context += f"等共{len(results)}个对象"
                        
                        await memory_tool.execute(
                            context=memory_context,
                            context_type="detection_result"
                        )
                        logger.info(f"检测结果已自动保存到记忆")
                except Exception as mem_error:
                    logger.warning(f"保存检测结果到记忆失败: {mem_error}")
            
            # 5. 保存到缓存
            self.cache_service.set('detection', image_path, response_text)
            logger.info(f"检测结果已缓存")
            
            return self.success_response(
                data=detection_data,
                message="检测完成",
                cached=False,
                image_path=image_path
            )
            
        except Exception as e:
            logger.error(f"检测失败: {e}", exc_info=True)
            raise DetectionError(
                message=f"检测失败: {str(e)}",
                error_code="DETECTION_FAILED",
                context={"image_path": image_path, "error": str(e)}
            )


class CacheTool(BaseTool):
    """缓存管理工具
    
    提供缓存清理和统计功能。
    """
    
    name: str = "manage_cache"
    description: str = "管理检测结果缓存"
    parameters: Dict[str, Any] = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "操作类型：clear（清理）或 stats（统计）",
                "enum": ["clear", "stats"]
            }
        },
        "required": ["action"]
    }
    
    cache_service: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """初始化缓存工具"""
        super().__init__(**data)
        
        if self.cache_service is None:
            self.cache_service = get_cache_service()
        
        logger.info(f"初始化缓存工具: {self.name}")
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """执行缓存管理
        
        Args:
            action: 操作类型（clear 或 stats）
            **kwargs: 其他参数
            
        Returns:
            ToolResult: 操作结果
        """
        try:
            if action == "clear":
                return await self._clear_cache()
            elif action == "stats":
                return await self._get_cache_stats()
            else:
                return self.fail_response(
                    error=f"不支持的操作: {action}",
                    error_code="INVALID_ACTION"
                )
        
        except Exception as e:
            logger.error(f"缓存操作失败: {e}")
            return self.fail_response(
                error=f"缓存操作失败: {str(e)}",
                error_code="CACHE_OPERATION_FAILED"
            )
    
    async def _clear_cache(self) -> ToolResult:
        """清理缓存"""
        try:
            count = self.cache_service.clear('detection')
            logger.info(f"已清理 {count} 个检测缓存")
            
            return self.success_response(
                data={"cleared_count": count},
                message=f"已清理 {count} 个检测缓存"
            )
        
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return self.fail_response(
                error=f"清理缓存失败: {str(e)}",
                error_code="CACHE_CLEAR_FAILED"
            )
    
    async def _get_cache_stats(self) -> ToolResult:
        """获取缓存统计"""
        try:
            stats = self.cache_service.get_stats()
            logger.info(f"获取缓存统计: {stats}")
            
            stats_text = f"""[STATS] 缓存统计信息:
缓存目录: {stats.get('cache_dir', 'N/A')}
缓存文件数: {stats.get('total_files', 0)}
总大小: {stats.get('total_size_mb', 0)} MB
过期时间: {stats.get('ttl_minutes', 0)} 分钟
"""
            
            return self.success_response(
                data=stats,
                message=stats_text
            )
        
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return self.fail_response(
                error=f"获取缓存统计失败: {str(e)}",
                error_code="CACHE_STATS_FAILED"
            )


# 工厂函数
def get_detection_tool() -> DetectionTool:
    """获取检测工具实例"""
    return DetectionTool()


def get_cache_tool() -> CacheTool:
    """获取缓存工具实例"""
    return CacheTool()
