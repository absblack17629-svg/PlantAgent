# -*- coding: utf-8 -*-
"""
九节点 LangGraph 工作流 + LangChain @tool
结合九节点架构和 LangChain 工具系统的优势
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from yoloapp.schema import Message
from yoloapp.utils.logger import get_logger
from yoloapp.tool.langchain_tools import get_all_tools

logger = get_logger(__name__)


# ==================== 状态定义 ====================
class NineNodeState(TypedDict):
    """九节点工作流状态"""
    # 输入
    user_input: str
    image_path: str | None
    
    # 消息历史
    messages: Annotated[Sequence[Message], add_messages]
    
    # 节点1: 意图识别结果
    intent: str
    emotion: str
    confidence: float
    
    # 节点2: 上下文
    context: str
    
    # 节点3: 记忆（跳过，简化）
    
    # 节点4: 工具规划
    tool_plan: list[str]  # 需要调用的工具名称列表
    
    # 节点5: 输入验证
    input_validation: dict
    
    # 节点6: 工具执行结果
    tool_results: dict  # 工具名 -> 结果
    
    # 节点7: 结果验证（跳过，简化）
    
    # 节点8: RAG 结果
    rag_results: list[str]
    
    # 节点9: 最终响应
    response: str


# ==================== 节点函数 ====================

async def node1_intent(state: NineNodeState) -> NineNodeState:
    """节点1: 意图识别"""
    logger.info(" [Node 1] 意图识别")
    
    from yoloapp.agent import IntentAgent
    from yoloapp.schema import Memory
    
    agent = IntentAgent()
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata["image_path"] = state.get("image_path")
    agent.memory = memory
    
    await agent.step()
    
    state["intent"] = memory.metadata.get("intent", "chat")
    state["emotion"] = memory.metadata.get("emotion", "neutral")
    state["confidence"] = memory.metadata.get("confidence", 0.7)
    
    logger.info(f"[OK] 意图: {state['intent']}")
    
    return state


async def node2_context(state: NineNodeState) -> NineNodeState:
    """节点2: 上下文管理（简化版）"""
    logger.info(" [Node 2] 上下文管理")
    
    # 简化：只记录基本信息
    context_parts = []
    
    if state.get("image_path"):
        context_parts.append(f"图片: {state['image_path']}")
    
    context_parts.append(f"意图: {state['intent']}")
    
    state["context"] = "\n".join(context_parts)
    
    logger.info(f"[OK] 上下文: {state['context']}")
    
    return state


async def node4_planning(state: NineNodeState) -> NineNodeState:
    """节点4: 工具规划"""
    logger.info(" [Node 4] 工具规划")
    
    intent = state.get("intent", "chat")
    image_path = state.get("image_path")
    
    tool_plan = []
    
    if intent == "detect" and image_path:
        # 检测意图：先检测，再分析
        tool_plan = ["detect_rice_disease", "analyze_detection_result"]
    elif intent == "query":
        # 查询意图：查询知识库
        tool_plan = ["query_agricultural_knowledge"]
    
    state["tool_plan"] = tool_plan
    
    logger.info(f"[OK] 规划: {tool_plan}")
    
    return state


async def node5_validation(state: NineNodeState) -> NineNodeState:
    """节点5: 输入验证"""
    logger.info(" [Node 5] 输入验证")
    
    intent = state.get("intent", "chat")
    image_path = state.get("image_path")
    
    validation = {"is_valid": True, "message": ""}
    
    if intent == "detect" and not image_path:
        validation = {
            "is_valid": False,
            "message": "检测病害需要提供图片"
        }
    
    state["input_validation"] = validation
    
    logger.info(f"[OK] 验证: {validation}")
    
    return state


async def node6_tool_execution(state: NineNodeState) -> NineNodeState:
    """节点6: 工具执行 - 使用 @tool 装饰的函数"""
    logger.info(" [Node 6] 工具执行")
    
    tool_plan = state.get("tool_plan", [])
    tool_results = {}
    
    # 获取所有工具
    tools = {tool.name: tool for tool in get_all_tools()}
    
    for tool_name in tool_plan:
        if tool_name not in tools:
            logger.warning(f" 工具不存在: {tool_name}")
            continue
        
        tool = tools[tool_name]
        
        try:
            # 根据工具准备参数
            if tool_name == "detect_rice_disease":
                result = await tool.ainvoke({"image_path": state["image_path"]})
            elif tool_name == "query_agricultural_knowledge":
                result = await tool.ainvoke({"question": state["user_input"]})
            elif tool_name == "analyze_detection_result":
                detection_result = tool_results.get("detect_rice_disease", "")
                result = await tool.ainvoke({
                    "detection_result": detection_result,
                    "user_question": state["user_input"]
                })
            else:
                result = "工具参数未配置"
            
            tool_results[tool_name] = result
            logger.info(f"[OK] {tool_name}: {len(str(result))} 字符")
            
        except Exception as e:
            logger.error(f"[FAIL] {tool_name} 失败: {e}")
            tool_results[tool_name] = f"执行失败: {str(e)}"
    
    state["tool_results"] = tool_results
    
    return state


async def node8_rag(state: NineNodeState) -> NineNodeState:
    """节点8: RAG 检索（如果需要）"""
    logger.info(" [Node 8] RAG 检索")
    
    # 如果已经有工具结果，可能不需要额外的 RAG
    # 这里简化处理
    state["rag_results"] = []
    
    logger.info("[OK] RAG 完成")
    
    return state


async def node9_response(state: NineNodeState) -> NineNodeState:
    """节点9: 响应生成"""
    logger.info(" [Node 9] 响应生成")
    
    intent = state.get("intent", "chat")
    tool_results = state.get("tool_results", {})
    
    # 根据意图和工具结果生成响应
    if intent == "chat":
        # 普通对话：使用 LLM 生成
        from yoloapp.llm import get_llm_client
        from yoloapp.prompt import CHAT_SYSTEM_PROMPT
        
        llm = get_llm_client()
        messages = [
            Message.system_message(CHAT_SYSTEM_PROMPT),
            Message.user_message(state["user_input"])
        ]
        response = await llm.ask(messages)
    
    elif tool_results:
        # 有工具结果：组合结果
        response_parts = []
        
        for tool_name, result in tool_results.items():
            if result and len(str(result)) > 10:
                response_parts.append(str(result))
        
        response = "\n\n".join(response_parts) if response_parts else "处理完成"
    
    else:
        response = "收到您的消息"
    
    state["response"] = response
    
    logger.info(f"[OK] 响应: {len(response)} 字符")
    
    return state


# ==================== 路由函数 ====================

def should_use_fast_path(state: NineNodeState) -> Literal["fast_path", "full_pipeline"]:
    """判断是否使用快速通道"""
    intent = state.get("intent", "chat")
    
    if intent in ["greet", "goodbye", "chat"]:
        logger.info("[ZAP] 快速通道")
        return "fast_path"
    
    logger.info("[Node 6] 完整流程")
    return "full_pipeline"


def should_skip_tools(state: NineNodeState) -> Literal["skip_tools", "execute_tools"]:
    """判断是否需要执行工具"""
    validation = state.get("input_validation", {})
    
    if not validation.get("is_valid", True):
        logger.info("[WARN] 验证失败，跳过工具")
        return "skip_tools"
    
    tool_plan = state.get("tool_plan", [])
    if not tool_plan:
        logger.info(" 无工具需要执行")
        return "skip_tools"
    
    return "execute_tools"


# ==================== 构建工作流 ====================

def create_nine_node_graph() -> StateGraph:
    """创建九节点工作流"""
    
    workflow = StateGraph(NineNodeState)
    
    # 添加节点
    workflow.add_node("node1_intent", node1_intent)
    workflow.add_node("node2_context", node2_context)
    workflow.add_node("node4_planning", node4_planning)
    workflow.add_node("node5_validation", node5_validation)
    workflow.add_node("node6_tool_execution", node6_tool_execution)
    workflow.add_node("node8_rag", node8_rag)
    workflow.add_node("node9_response", node9_response)
    
    # 设置入口
    workflow.set_entry_point("node1_intent")
    
    # 意图识别后，选择路径
    workflow.add_conditional_edges(
        "node1_intent",
        should_use_fast_path,
        {
            "fast_path": "node9_response",  # 快速通道
            "full_pipeline": "node2_context"  # 完整流程
        }
    )
    
    # 完整流程
    workflow.add_edge("node2_context", "node4_planning")
    workflow.add_edge("node4_planning", "node5_validation")
    
    # 验证后，判断是否执行工具
    workflow.add_conditional_edges(
        "node5_validation",
        should_skip_tools,
        {
            "skip_tools": "node9_response",  # 跳过工具
            "execute_tools": "node6_tool_execution"  # 执行工具
        }
    )
    
    workflow.add_edge("node6_tool_execution", "node8_rag")
    workflow.add_edge("node8_rag", "node9_response")
    
    # 响应生成后结束
    workflow.add_edge("node9_response", END)
    
    # 编译
    app = workflow.compile()
    
    logger.info("[OK] 九节点工作流构建完成")
    
    return app


# ==================== 便捷函数 ====================

async def run_nine_node_workflow(
    user_input: str,
    image_path: str | None = None
) -> dict:
    """
    运行九节点工作流
    
    Args:
        user_input: 用户输入
        image_path: 图片路径（可选）
        
    Returns:
        包含响应的字典
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"[ROCKET] 启动九节点工作流（LangGraph + @tool）")
    logger.info(f"{'='*60}")
    
    try:
        # 创建工作流
        app = create_nine_node_graph()
        
        # 初始化状态
        initial_state: NineNodeState = {
            "user_input": user_input,
            "image_path": image_path,
            "messages": [],
            "intent": "",
            "emotion": "",
            "confidence": 0.0,
            "context": "",
            "tool_plan": [],
            "input_validation": {},
            "tool_results": {},
            "rag_results": [],
            "response": ""
        }
        
        # 运行工作流
        final_state = await app.ainvoke(initial_state)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"[OK] 九节点工作流完成")
        logger.info(f"{'='*60}")
        
        return {
            "success": True,
            "response": final_state["response"],
            "intent": final_state["intent"],
            "emotion": final_state["emotion"],
            "tool_results": final_state["tool_results"],
            "agent_mode": "nine_node_with_tools",
            "state": final_state
        }
        
    except Exception as e:
        logger.error(f"[FAIL] 工作流失败: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "response": f"处理失败: {str(e)}",
            "error": str(e),
            "agent_mode": "error"
        }
