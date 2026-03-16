# -*- coding: utf-8 -*-
"""
LangGraph 编排工作流
用户提问 → 输入验证 → ContextAgent → PlantAgent → 输出验证 → 输出

PlantAgent 具备 ReAct 能力：自动选择工具、执行工具、观察结果
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from yoloapp.schema import Message
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


# ==================== 状态定义 ====================
class WorkflowState(TypedDict):
    """工作流状态"""

    messages: Annotated[list, add_messages]
    user_input: str
    image_path: Optional[str]
    validation_result: Optional[dict]
    context_summary: Optional[str]
    plant_agent_results: Optional[list]
    final_response: Optional[str]
    error: Optional[str]


# ==================== 节点函数 ====================


def input_validation_node(state: WorkflowState) -> WorkflowState:
    """
    输入验证节点
    验证用户输入是否有效
    """
    logger.info("[Node] 输入验证...")

    user_input = state.get("user_input", "")
    image_path = state.get("image_path")

    is_valid = True
    error_msg = ""

    if not user_input or len(user_input.strip()) == 0:
        is_valid = False
        error_msg = "输入为空"
    elif len(user_input) > 2000:
        is_valid = False
        error_msg = "输入过长"

    state["validation_result"] = {
        "is_valid": is_valid,
        "error": error_msg,
    }

    logger.info(f"[Node] 输入验证 {'通过' if is_valid else '失败'}: {error_msg}")
    return state


def context_agent_node(state: WorkflowState) -> WorkflowState:
    """
    ContextAgent 节点
    对话压缩（超过3轮时）
    """
    logger.info("[Node] ContextAgent 处理...")

    messages = state.get("messages", [])
    conversation_history = messages[:-1]  # 排除最新消息

    if len(conversation_history) >= 6:  # 3对对话
        logger.info("执行对话压缩...")
        summary = "之前对话摘要:\n"
        for msg in conversation_history[-6:]:
            role = getattr(msg, "role", "unknown")
            content = getattr(msg, "content", "")[:80]
            summary += f"- {role}: {content}...\n"
        state["context_summary"] = summary
    else:
        state["context_summary"] = None

    logger.info("[Node] ContextAgent 完成")
    return state


def plant_agent_node(state: WorkflowState) -> WorkflowState:
    """
    PlantAgent 节点
    具备 ReAct 能力：自动选择工具、执行工具、观察结果
    """
    logger.info("[Node] PlantAgent 处理（ReAct 模式）...")

    import asyncio
    from yoloapp.agent.plant_agent import PlantAgent
    from yoloapp.schema import Memory

    user_input = state.get("user_input", "")
    image_path = state.get("image_path")
    context_summary = state.get("context_summary")

    # 构建上下文信息
    context_info = f"\n上下文摘要: {context_summary}" if context_summary else ""

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def _run():
        # 创建 Memory
        memory = Memory()
        memory.add_message(Message(role="user", content=user_input + context_info))
        memory.metadata["image_path"] = image_path

        # 创建 PlantAgent（ReAct 模式）
        agent = PlantAgent(max_iterations=5)
        agent.memory = memory

        # 执行（ReAct 循环：reason → act → observe → repeat）
        response = await agent.step()

        return {
            "response": response,
            "execution_results": memory.metadata.get("execution_results", []),
        }

    try:
        result = loop.run_until_complete(_run())

        state["plant_agent_results"] = result["execution_results"]
        state["final_response"] = result["response"]

        # 获取工具调用记录
        tools_called = [r.get("tool") for r in result["execution_results"]]
        logger.info(f"[Node] PlantAgent 完成，调用工具: {tools_called}")

    except Exception as e:
        logger.error(f"PlantAgent 执行失败: {e}")
        state["plant_agent_results"] = []
        state["error"] = str(e)

    return state


def output_validation_node(state: WorkflowState) -> WorkflowState:
    """
    输出验证节点
    验证 PlantAgent 返回的结果是否有效
    """
    logger.info("[Node] 输出验证...")

    results = state.get("plant_agent_results", [])
    final_response = state.get("final_response")

    is_valid = True
    error_msg = ""

    # 如果没有工具结果，检查是否有直接响应（如简单对话）
    if not results:
        if final_response:
            # 有直接响应，不需要工具（如打招呼）
            is_valid = True
            error_msg = "直接响应"
        else:
            # 既没有工具结果也没有直接响应
            is_valid = False
            error_msg = "没有执行任何工具"
    else:
        # 有工具结果，检查是否有错误
        for r in results:
            if "error" in r and r.get("error"):
                is_valid = False
                error_msg = f"工具执行错误: {r.get('error')}"
                break

    validation = state.get("validation_result", {})
    validation["output_valid"] = is_valid
    validation["output_error"] = error_msg
    state["validation_result"] = validation

    logger.info(f"[Node] 输出验证 {'通过' if is_valid else '失败'}: {error_msg}")
    return state


def response_node(state: WorkflowState) -> WorkflowState:
    """
    输出节点
    PlantAgent 已经生成最终响应，直接返回
    """
    logger.info("[Node] 生成最终响应...")

    # PlantAgent 已经生成了完整响应
    results = state.get("plant_agent_results", [])

    if results:
        # 从结果中获取 PlantAgent 的最终响应
        # PlantAgent 会将响应放在最后一个工具结果中或单独返回
        for r in reversed(results):
            if r.get("result"):
                state["final_response"] = r.get("result")
                break

    if not state.get("final_response"):
        state["final_response"] = "处理完成"

    logger.info("[Node] 响应生成完成")
    return state


def error_handler_node(state: WorkflowState) -> WorkflowState:
    """错误处理节点"""
    validation = state.get("validation_result", {})

    if not validation.get("is_valid"):
        state["final_response"] = (
            f"抱歉，您的输入有问题：{validation.get('error')}。请重新输入。"
        )
    elif not validation.get("output_valid"):
        state["final_response"] = (
            f"处理过程中遇到问题：{validation.get('output_error')}。请稍后重试。"
        )
    else:
        state["final_response"] = "处理过程中遇到未知错误，请稍后重试。"

    logger.error(f"[Node] 错误处理: {state['final_response']}")
    return state


# ==================== 创建工作流 ====================
def create_langgraph_workflow():
    """
    创建 LangGraph 工作流

    流程：输入验证 → ContextAgent → PlantAgent(ReAct) → 输出验证 → 输出
    """
    logger.info("创建 LangGraph 工作流...")

    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("context_agent", context_agent_node)
    workflow.add_node("plant_agent", plant_agent_node)
    workflow.add_node("output_validation", output_validation_node)
    workflow.add_node("response", response_node)
    workflow.add_node("error_handler", error_handler_node)

    # 设置入口
    workflow.set_entry_point("input_validation")

    # 条件边：输入验证
    workflow.add_conditional_edges(
        "input_validation",
        lambda state: (
            "context_agent"
            if state.get("validation_result", {}).get("is_valid")
            else "error_handler"
        ),
    )

    # 正常流程
    workflow.add_edge("context_agent", "plant_agent")
    workflow.add_edge("plant_agent", "output_validation")

    # 条件边：输出验证
    workflow.add_conditional_edges(
        "output_validation",
        lambda state: (
            "response"
            if state.get("validation_result", {}).get("output_valid")
            else "error_handler"
        ),
    )

    # 结束
    workflow.add_edge("response", END)
    workflow.add_edge("error_handler", END)

    app = workflow.compile()
    logger.info("[OK] LangGraph 工作流创建完成")

    return app


# ==================== 运行工作流 ====================
async def run_langgraph_workflow(
    user_input: str, image_path: str | None = None
) -> dict:
    """
    运行 LangGraph 工作流

    Args:
        user_input: 用户输入
        image_path: 图片路径（可选）

    Returns:
        包含响应的字典
    """
    logger.info(f"\n{'=' * 60}")
    logger.info(f"🚀 启动 LangGraph 工作流")
    logger.info(f"用户输入: {user_input}")
    logger.info(f"图片路径: {image_path}")
    logger.info(f"{'=' * 60}")

    try:
        app = create_langgraph_workflow()

        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_input": user_input,
            "image_path": image_path,
        }

        result = await app.ainvoke(initial_state)

        final_response = result.get("final_response", "处理完成")
        tool_results = result.get("plant_agent_results", [])

        logger.info(f"\n{'=' * 60}")
        logger.info(f"[OK] 工作流执行完成")
        logger.info(f"{'=' * 60}")

        return {
            "success": True,
            "response": final_response,
            "tool_results": tool_results,
            "agent_mode": "langgraph_workflow",
        }

    except Exception as e:
        logger.error(f"[FAIL] 工作流执行失败: {e}")
        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "response": f"处理失败: {str(e)}",
            "error": str(e),
            "agent_mode": "langgraph_workflow_error",
        }

    if is_valid:
        logger.info(f"[Node] 输入验证通过")
    else:
        logger.warning(f"[Node] 输入验证失败: {error_msg}")

    return state


# ==================== 创建工作流 ====================
def create_langgraph_workflow():
    """
    创建 LangGraph 工作流

    流程：输入验证 → ContextAgent → PlantAgent(ReAct) → 输出验证 → 输出
    """
    logger.info("创建 LangGraph 工作流...")

    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("context_agent", context_agent_node)
    workflow.add_node("plant_agent", plant_agent_node)
    workflow.add_node("output_validation", output_validation_node)
    workflow.add_node("response", response_node)
    workflow.add_node("error_handler", error_handler_node)

    # 设置入口
    workflow.set_entry_point("input_validation")

    # 条件边：输入验证
    workflow.add_conditional_edges(
        "input_validation",
        lambda state: (
            "context_agent"
            if state.get("validation_result", {}).get("is_valid")
            else "error_handler"
        ),
    )

    # 正常流程
    workflow.add_edge("context_agent", "plant_agent")
    workflow.add_edge("plant_agent", "output_validation")

    # 条件边：输出验证
    workflow.add_conditional_edges(
        "output_validation",
        lambda state: (
            "response"
            if state.get("validation_result", {}).get("output_valid")
            else "error_handler"
        ),
    )

    # 结束
    workflow.add_edge("response", END)
    workflow.add_edge("error_handler", END)

    app = workflow.compile()
    logger.info("[OK] LangGraph 工作流创建完成")

    return app


# ==================== 运行工作流 ====================
async def run_langgraph_workflow(
    user_input: str, image_path: str | None = None
) -> dict:
    """
    运行 LangGraph 工作流

    Args:
        user_input: 用户输入
        image_path: 图片路径（可选）

    Returns:
        包含响应的字典
    """
    logger.info(f"\n{'=' * 60}")
    logger.info(f"启动 LangGraph 工作流")
    logger.info(f"用户输入: {user_input}")
    logger.info(f"图片路径: {image_path}")
    logger.info(f"{'=' * 60}")

    try:
        app = create_langgraph_workflow()

        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_input": user_input,
            "image_path": image_path,
        }

        result = await app.ainvoke(initial_state)

        final_response = result.get("final_response", "处理完成")
        tool_results = result.get("plant_agent_results", [])

        logger.info(f"\n{'=' * 60}")
        logger.info(f"[OK] 工作流执行完成")
        logger.info(f"{'=' * 60}")

        return {
            "success": True,
            "response": final_response,
            "tool_results": tool_results,
            "agent_mode": "langgraph_workflow",
        }

    except Exception as e:
        logger.error(f"[FAIL] 工作流执行失败: {e}")
        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "response": f"处理失败: {str(e)}",
            "error": str(e),
            "agent_mode": "langgraph_workflow_error",
        }

        return {
            "success": True,
            "response": final_response,
            "intent": result.get("intent"),
            "tool_results": result.get("tool_results", []),
            "agent_mode": "langgraph_workflow",
        }

    except Exception as e:
        logger.error(f"[FAIL] 工作流执行失败: {e}")
        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "response": f"处理失败: {str(e)}",
            "error": str(e),
            "agent_mode": "langgraph_workflow_error",
        }
