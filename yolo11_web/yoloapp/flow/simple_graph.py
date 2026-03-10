# -*- coding: utf-8 -*-
"""
简化的 LangGraph 工作流
使用 LangChain 的 @tool 装饰器和 create_react_agent
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

from yoloapp.schema import Message
from yoloapp.utils.logger import get_logger
from yoloapp.tool.langchain_tools import get_all_tools
from yoloapp.llm import get_llm_client

logger = get_logger(__name__)


# ==================== 状态定义 ====================
class AgentState(TypedDict):
    """Agent 状态"""
    messages: Annotated[Sequence[Message], add_messages]
    user_input: str
    image_path: str | None


# ==================== 创建 Agent ====================
def create_agent():
    """创建 ReAct Agent"""
    
    # 获取 LLM
    llm = get_llm_client()
    
    # 获取所有工具
    tools = get_all_tools()
    
    logger.info(f"[OK] 创建 Agent，包含 {len(tools)} 个工具")
    
    # 系统提示词
    system_prompt = """你是一位专业的水稻病害智能助手。

你的职责：
1. 当用户上传图片时，使用 detect_rice_disease 工具检测病害
2. 当用户询问农业知识时，使用 query_agricultural_knowledge 工具查询
3. 检测完成后，使用 analyze_detection_result 工具提供详细分析

注意事项：
- 如果用户提供了图片路径，优先使用检测工具
- 检测后要提供防治建议
- 回答要专业但易懂
- 使用中文回复
"""
    
    # 创建 ReAct Agent
    # 参数：model, tools, state_modifier (可选)
    agent = create_react_agent(llm, tools)
    
    return agent


# ==================== 便捷函数 ====================
async def run_agent(user_input: str, image_path: str | None = None) -> dict:
    """
    运行 Agent
    
    Args:
        user_input: 用户输入
        image_path: 图片路径（可选）
        
    Returns:
        包含响应的字典
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 启动简化 Agent")
    logger.info(f"{'='*60}")
    logger.info(f"用户输入: {user_input}")
    logger.info(f"图片路径: {image_path}")
    
    try:
        # 创建 Agent
        agent = create_agent()
        
        # 构建消息
        messages = []
        
        # 添加系统提示词
        system_prompt = """你是一位专业的水稻病害智能助手。

你的职责：
1. 当用户上传图片时，使用 detect_rice_disease 工具检测病害
2. 当用户询问农业知识时，使用 query_agricultural_knowledge 工具查询
3. 检测完成后，使用 analyze_detection_result 工具提供详细分析

注意事项：
- 如果用户提供了图片路径，优先使用检测工具
- 检测后要提供防治建议
- 回答要专业但易懂
- 使用中文回复
"""
        messages.append({"role": "system", "content": system_prompt})
        
        # 如果有图片，在消息中说明
        if image_path:
            user_message = f"{user_input}\n\n[图片路径: {image_path}]"
        else:
            user_message = user_input
        
        messages.append({"role": "user", "content": user_message})
        
        # 运行 Agent
        result = await agent.ainvoke({"messages": messages})
        
        # 获取最后一条消息（Agent 的回复）
        final_messages = result.get("messages", [])
        if final_messages:
            last_message = final_messages[-1]
            response = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response = "处理完成，但没有生成回复"
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[OK] Agent 执行完成")
        logger.info(f"{'='*60}")
        
        return {
            "success": True,
            "response": response,
            "agent_mode": "simple_react_agent",
            "messages": final_messages
        }
        
    except Exception as e:
        logger.error(f"[FAIL] Agent 执行失败: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "response": f"处理失败: {str(e)}",
            "error": str(e),
            "agent_mode": "error"
        }
