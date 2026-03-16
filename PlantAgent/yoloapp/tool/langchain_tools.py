# -*- coding: utf-8 -*-
"""
LangChain 工具定义
使用 @tool 装饰器定义工具，让 LangGraph 自动发现和调用
"""

from langchain_core.tools import tool
from typing import Optional
from yoloapp.utils.logger import get_logger
from yoloapp.schema import Message

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


@tool
async def web_search(query: str) -> str:
    """
    网络检索工具

    用于补充最新信息或本地知识库没有的内容。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果或提示信息
    """
    try:
        logger.info(f"[SEARCH] 网络检索: {query}")

        # 尝试 Tavily AI 搜索
        try:
            from tavily import TavilyClient
            from config.settings import settings

            api_key = settings.TAVILY_API_KEY
            if not api_key:
                return "Tavily API Key 未配置，请在 .env 中设置 TAVILY_API_KEY"

            tavily = TavilyClient(api_key=api_key)
            response = tavily.search(
                query=query,
                max_results=5,
                include_answer=True,
                include_raw_content=False,
            )

            results = response.get("results", [])
            if results and len(results) > 0:
                summary = f"网络检索结果（{len(results)}条）：\n\n"
                for i, r in enumerate(results, 1):
                    title = r.get("title", "")[:70]
                    content = r.get("content", "")[:200]
                    url = r.get("url", "")
                    summary += f"{i}. {title}\n{content}...\n来源: {url}\n\n"
                return summary
            else:
                # 无结果尝试简单搜索
                simple_response = tavily.search(query=query, max_results=3)
                simple_results = simple_response.get("results", [])
                if simple_results:
                    summary = f"网络检索结果（{len(simple_results)}条）：\n\n"
                    for i, r in enumerate(simple_results, 1):
                        title = r.get("title", "")[:70]
                        content = r.get("content", "")[:200]
                        url = r.get("url", "")
                        summary += f"{i}. {title}\n{content}...\n来源: {url}\n\n"
                    return summary

        except ImportError:
            logger.warning("Tavily 未安装，尝试备用方案")
            return "网络检索功能需要安装 tavily-python：pip install tavily-python"
        except Exception as e:
            logger.warning(f"Tavily 搜索异常: {e}")

        # 备用：返回提示
        return f"""网络检索暂时不可用。

当前网络环境可能无法访问 Tavily。

建议：
• 使用 query_agricultural_knowledge 工具查询本地知识库
• 或手动访问 https://www.tavily.com/search?q={query}

搜索词: {query}"""

    except Exception as e:
        logger.error(f"网络检索失败: {e}")
        return f"网络检索失败: {str(e)}"


@tool
async def summarize_polish(all_results: str, user_question: str) -> str:
    """
    汇总润色工具

    将所有工具返回的结果汇总，用人性化、友好的语言重写。

    Args:
        all_results: 所有工具返回的结果汇总
        user_question: 用户的原始问题

    Returns:
        润色后的最终回答
    """
    try:
        logger.info("[POLISH] 开始汇总润色...")

        # 使用 LLM 进行润色
        from yoloapp.llm import get_llm_client

        llm = get_llm_client()

        polish_prompt = f"""请将以下工具返回的结果进行汇总润色，用人性化、友好的语言重写：

用户问题：{user_question}

工具结果：
{all_results}

要求：
1. 用第一人称"我"或"我们"来回答
2. 语言亲切、自然，像专家朋友在聊天
3. 结构清晰，适当使用emoji
4. 保留关键信息，去除冗余
5. 如果结果中有病害名称、防治方法等重要信息，必须包含

请直接返回润色后的回答："""

        response = await llm.ask(
            [Message.system_message(polish_prompt), Message.user_message("请润色")]
        )

        result = response.content if hasattr(response, "content") else str(response)

        logger.info(f"[OK] 润色完成: {len(result)} 字符")

        return result

    except Exception as e:
        error_msg = f"润色失败: {str(e)}"
        logger.error(error_msg)
        # 如果润色失败，返回原始结果
        return all_results


# 导出所有工具
def get_all_tools():
    """获取所有可用的工具"""
    return [
        detect_rice_disease,
        query_agricultural_knowledge,
        analyze_detection_result,
        web_search,
        summarize_polish,
    ]
