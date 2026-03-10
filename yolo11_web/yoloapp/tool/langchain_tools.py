# -*- coding: utf-8 -*-
"""
LangChain 工具定义
使用 @tool 装饰器定义工具，让 LangGraph 自动发现和调用
"""

from langchain_core.tools import tool
from typing import Optional
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


@tool
async def detect_rice_disease(image_path: str) -> str:
    """
    检测水稻病害
    
    使用 YOLO11 模型检测图片中的水稻病害。
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        检测结果描述，包含病害类型和位置
    """
    try:
        logger.info(f"[DETECT] 开始检测图片: {image_path}")
        
        # 导入检测服务
        from services.detection_service import DetectionService
        
        # 创建检测服务实例
        detection_service = DetectionService()
        
        # 执行检测（正确的方法名是 detect_objects）
        results = await detection_service.detect_objects(image_path)
        
        if not results or len(results) == 0:
            return "未检测到任何病害"
        
        # 格式化结果
        disease_count = {}
        for result in results:
            # 兼容中英文键名
            disease = result.get("class_name") or result.get("类别", "未知")
            disease_count[disease] = disease_count.get(disease, 0) + 1
        
        # 构建描述
        description = f"检测到 {len(results)} 个病害区域：\n"
        for disease, count in disease_count.items():
            description += f"- {disease}: {count} 处\n"
        
        logger.info(f"[OK] 检测完成: {description}")
        
        return description
        
    except Exception as e:
        error_msg = f"检测失败: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return error_msg


@tool
async def query_agricultural_knowledge(question: str) -> str:
    """
    查询农业知识库
    
    从知识库中检索水稻病害防治相关知识。
    
    Args:
        question: 用户问题
        
    Returns:
        知识库检索结果
    """
    try:
        logger.info(f"[QUERY] 查询知识库: {question}")
        
        # 导入 RAG 服务
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client
        
        # 获取服务
        rag_service = get_rag_service()
        llm = get_llm_client()
        
        # 确保 RAG 已初始化
        if not rag_service._initialized:
            logger.info("[INFO] RAG服务未初始化，正在初始化...")
            await rag_service.init_async()
            
            # 再次检查是否初始化成功
            if not rag_service._initialized:
                logger.warning("[WARN] RAG服务初始化失败")
                return "抱歉，知识库系统暂未初始化，请稍后重试。"
        
        # 查询知识库
        answer = await rag_service.query(question, llm)
        
        logger.info(f"[OK] 知识库查询完成: {len(answer)} 字符")
        
        return answer
        
    except Exception as e:
        error_msg = f"知识库查询失败: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return error_msg


@tool
async def analyze_detection_result(detection_result: str, user_question: str) -> str:
    """
    分析检测结果并提供建议
    
    基于检测结果和用户问题，提供详细的病害分析和防治建议。
    
    Args:
        detection_result: 检测结果描述
        user_question: 用户的原始问题
        
    Returns:
        分析结果和防治建议
    """
    try:
        logger.info(f"[SEARCH] 分析检测结果...")
        
        # 导入 RAG 服务
        from yoloapp.rag import get_rag_service
        from yoloapp.llm import get_llm_client
        
        # 获取服务
        rag_service = get_rag_service()
        llm = get_llm_client()
        
        # 确保 RAG 已初始化
        if not rag_service._initialized:
            logger.info("[INFO] RAG服务未初始化，正在初始化...")
            await rag_service.init_async()
            
            # 再次检查是否初始化成功
            if not rag_service._initialized:
                logger.warning("[WARN] RAG服务初始化失败，使用基础分析")
                return f"基础分析：检测到{detection_result}。建议查阅相关农业资料或咨询专家。"
        
        # 构建分析问题
        analysis_question = f"""
        检测结果：{detection_result}
        
        用户问题：{user_question}
        
        请基于检测结果提供详细的病害分析和防治建议。
        """
        
        # 查询知识库
        answer = await rag_service.query(analysis_question, llm)
        
        logger.info(f"[OK] 分析完成: {len(answer)} 字符")
        
        return answer
        
    except Exception as e:
        error_msg = f"分析失败: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())
        return error_msg


# 导出所有工具
def get_all_tools():
    """获取所有可用的工具"""
    return [
        detect_rice_disease,
        query_agricultural_knowledge,
        analyze_detection_result
    ]
