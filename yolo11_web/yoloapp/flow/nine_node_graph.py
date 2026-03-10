# -*- coding: utf-8 -*-
"""
九节点 LangGraph 工作流
使用 LangGraph 实现清晰的状态图工作流
"""

from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from yoloapp.schema import Message
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


# ==================== 状态定义 ====================
class NineNodeState(TypedDict):
    """九节点工作流状态"""
    # 输入
    user_input: str
    image_path: str | None
    
    # 消息历史
    messages: Annotated[Sequence[Message], add_messages]
    
    # 意图识别结果
    intent: str
    emotion: str
    confidence: float
    
    # 上下文
    context: str
    
    # 验证结果
    input_validation: dict
    
    # 工具规划和执行
    tool_plan: list[dict]
    tool_results: list[dict]
    
    # RAG 结果
    rag_results: list[str]
    
    # 最终响应
    response: str
    
    # 元数据
    metadata: dict


# ==================== 节点函数 ====================

async def intent_node(state: NineNodeState) -> NineNodeState:
    """节点1: 意图识别"""
    from yoloapp.agent import IntentAgent
    
    logger.info("[TARGET] [Node 1] 意图识别...")
    
    agent = IntentAgent()
    # 创建临时 Memory
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata["image_path"] = state.get("image_path")
    agent.memory = memory
    
    # 执行意图识别
    await agent.step()
    
    # 更新状态
    state["intent"] = memory.metadata.get("intent", "chat")
    state["emotion"] = memory.metadata.get("emotion", "neutral")
    state["confidence"] = memory.metadata.get("confidence", 0.7)
    
    logger.info(f"[SUCCESS] 意图: {state['intent']}, 情感: {state['emotion']}")
    
    return state


async def context_node(state: NineNodeState) -> NineNodeState:
    """节点2: 上下文管理"""
    from yoloapp.agent import ContextAgent
    
    logger.info("📚 [Node 2] 上下文管理...")
    
    # 获取 skill_client
    skill_client = state.get("metadata", {}).get("skill_client")
    
    agent = ContextAgent(skill_client=skill_client)
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "image_path": state.get("image_path"),
        "intent": state.get("intent")
    })
    agent.memory = memory
    
    # 执行上下文加载
    context = await agent.step()
    
    state["context"] = context
    logger.info(f"[SUCCESS] 上下文加载完成: {len(context)} 字符")
    
    return state


async def memory_node(state: NineNodeState) -> NineNodeState:
    """节点3: 记忆管理"""
    from yoloapp.agent import MemoryAgent
    
    logger.info("💾 [Node 3] 记忆管理...")
    
    # 获取 skill_client
    skill_client = state.get("metadata", {}).get("skill_client")
    
    agent = MemoryAgent(skill_client=skill_client)
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "intent": state.get("intent"),
        "context": state.get("context")
    })
    agent.memory = memory
    
    # 执行记忆保存
    await agent.step()
    
    logger.info("[SUCCESS] 记忆保存完成")
    
    return state


async def planning_node(state: NineNodeState) -> NineNodeState:
    """节点4: 工具规划"""
    from yoloapp.agent import PlanningAgent
    
    logger.info("🗺️ [Node 4] 工具规划...")
    
    agent = PlanningAgent()
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "intent": state.get("intent"),
        "image_path": state.get("image_path")
    })
    agent.memory = memory
    
    # 执行工具规划
    await agent.step()
    
    state["tool_plan"] = memory.metadata.get("tool_plan", [])
    logger.info(f"[SUCCESS] 规划完成: {len(state['tool_plan'])} 个工具")
    
    return state


async def input_validation_node(state: NineNodeState) -> NineNodeState:
    """节点5: 输入验证"""
    from yoloapp.agent import InputValidationAgent
    
    logger.info("[SEARCH] [Node 5] 输入验证...")
    
    agent = InputValidationAgent()
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "intent": state.get("intent"),
        "image_path": state.get("image_path")
    })
    agent.memory = memory
    
    # 执行输入验证
    await agent.step()
    
    state["input_validation"] = memory.metadata.get("input_validation", {})
    
    if state["input_validation"].get("clarification_needed"):
        logger.warning("[WARNING] 输入不完整，需要澄清")
    else:
        logger.info("[SUCCESS] 输入验证通过")
    
    return state


async def tool_execution_node(state: NineNodeState) -> NineNodeState:
    """节点6: 工具执行"""
    from yoloapp.agent import ToolExecutionAgent
    
    logger.info("🔧 [Node 6] 工具执行...")
    
    # 获取 skill_client（从全局状态或创建新的）
    skill_client = state.get("metadata", {}).get("skill_client")
    
    agent = ToolExecutionAgent(skill_client=skill_client)
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "tool_plan": state.get("tool_plan", []),
        "image_path": state.get("image_path")
    })
    agent.memory = memory
    
    # 执行工具
    await agent.step()
    
    state["tool_results"] = memory.metadata.get("tool_results", [])
    logger.info(f"[SUCCESS] 工具执行完成: {len(state['tool_results'])} 个结果")
    
    return state


async def result_validation_node(state: NineNodeState) -> NineNodeState:
    """节点7: 结果验证"""
    from yoloapp.agent import ResultValidationAgent
    
    logger.info("✔️ [Node 7] 结果验证...")
    
    agent = ResultValidationAgent()
    from yoloapp.schema import Memory
    memory = Memory()
    memory.metadata["tool_results"] = state.get("tool_results", [])
    agent.memory = memory
    
    # 执行结果验证
    await agent.step()
    
    logger.info("[SUCCESS] 结果验证完成")
    
    return state


async def rag_node(state: NineNodeState) -> NineNodeState:
    """节点8: RAG 检索"""
    from yoloapp.agent import RAGAgent
    
    logger.info("🔎 [Node 8] RAG 检索...")
    
    # 获取 skill_client
    skill_client = state.get("metadata", {}).get("skill_client")
    
    agent = RAGAgent(skill_client=skill_client)
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "intent": state.get("intent"),
        "tool_results": state.get("tool_results", [])
    })
    agent.memory = memory
    
    # 执行 RAG 检索
    await agent.step()
    
    state["rag_results"] = memory.metadata.get("rag_results", [])
    logger.info(f"[SUCCESS] RAG 检索完成: {len(state['rag_results'])} 个结果")
    
    return state


async def response_node(state: NineNodeState) -> NineNodeState:
    """节点9: 响应生成"""
    from yoloapp.agent import ResponseAgent
    
    logger.info("💬 [Node 9] 响应生成...")
    
    agent = ResponseAgent()
    from yoloapp.schema import Memory
    memory = Memory()
    memory.add_message(Message.user_message(state["user_input"]))
    memory.metadata.update({
        "intent": state.get("intent"),
        "emotion": state.get("emotion"),
        "image_path": state.get("image_path"),
        "tool_results": state.get("tool_results", []),
        "rag_results": state.get("rag_results", []),
        "input_validation": state.get("input_validation", {})
    })
    agent.memory = memory
    
    # 执行响应生成
    response = await agent.step()
    
    state["response"] = response
    logger.info(f"[SUCCESS] 响应生成完成: {len(response)} 字符")
    
    return state


# ==================== 路由函数 ====================

def should_use_fast_path(state: NineNodeState) -> Literal["fast_path", "full_pipeline"]:
    """判断是否使用快速通道"""
    intent = state.get("intent", "chat")
    
    # 普通对话使用快速通道
    if intent in ["greet", "goodbye", "chat"]:
        logger.info("⚡ 使用快速通道")
        return "fast_path"
    
    # 检测和查询使用完整流程
    logger.info("🔧 使用完整流程")
    return "full_pipeline"


def should_skip_to_response(state: NineNodeState) -> Literal["skip_to_response", "continue"]:
    """判断是否需要跳过工具执行直接生成响应"""
    validation = state.get("input_validation", {})
    
    if validation.get("clarification_needed"):
        logger.info("[WARNING] 需要澄清，跳过工具执行")
        return "skip_to_response"
    
    return "continue"


# ==================== 构建工作流图 ====================

def create_nine_node_graph() -> StateGraph:
    """创建九节点 LangGraph 工作流"""
    
    # 创建状态图
    workflow = StateGraph(NineNodeState)
    
    # 添加节点
    workflow.add_node("intent", intent_node)
    workflow.add_node("context", context_node)
    workflow.add_node("memory", memory_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("input_validation", input_validation_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("result_validation", result_validation_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("response", response_node)
    
    # 设置入口点
    workflow.set_entry_point("intent")
    
    # 添加边（工作流路径）
    # 意图识别后，根据意图类型选择路径
    workflow.add_conditional_edges(
        "intent",
        should_use_fast_path,
        {
            "fast_path": "response",  # 快速通道：直接生成响应
            "full_pipeline": "context"  # 完整流程：继续后续节点
        }
    )
    
    # 完整流程的顺序执行
    workflow.add_edge("context", "memory")
    workflow.add_edge("memory", "planning")
    workflow.add_edge("planning", "input_validation")
    
    # 输入验证后，判断是否需要澄清
    workflow.add_conditional_edges(
        "input_validation",
        should_skip_to_response,
        {
            "skip_to_response": "response",  # 需要澄清：跳到响应
            "continue": "tool_execution"  # 继续执行工具
        }
    )
    
    workflow.add_edge("tool_execution", "result_validation")
    workflow.add_edge("result_validation", "rag")
    workflow.add_edge("rag", "response")
    
    # 响应生成后结束
    workflow.add_edge("response", END)
    
    # 编译图
    app = workflow.compile()
    
    logger.info("[SUCCESS] LangGraph 工作流构建完成")
    
    return app


# ==================== 便捷函数 ====================

async def run_nine_node_workflow(
    user_input: str,
    image_path: str | None = None,
    skill_client = None
) -> dict:
    """
    运行九节点工作流
    
    Args:
        user_input: 用户输入
        image_path: 图片路径（可选）
        skill_client: Skill 客户端（可选）
        
    Returns:
        包含响应和处理信息的字典
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"🚀 启动 LangGraph 九节点工作流")
    logger.info(f"{'='*60}")
    
    # 如果没有提供 skill_client，尝试获取
    if skill_client is None:
        try:
            from skill_client import get_skill_client
            skill_client = get_skill_client()
            logger.info("[SUCCESS] 获取 skill_client 成功")
        except Exception as e:
            logger.warning(f"[WARNING] 无法获取 skill_client: {e}")
    
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
        "input_validation": {},
        "tool_plan": [],
        "tool_results": [],
        "rag_results": [],
        "response": "",
        "metadata": {
            "skill_client": skill_client  # 将 skill_client 放入 metadata
        }
    }
    
    # 运行工作流
    final_state = await app.ainvoke(initial_state)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"[SUCCESS] LangGraph 工作流执行完成")
    logger.info(f"{'='*60}")
    
    # 返回结果
    return {
        "success": True,
        "response": final_state["response"],
        "intent": final_state["intent"],
        "emotion": final_state["emotion"],
        "confidence": final_state["confidence"],
        "tool_results": final_state["tool_results"],
        "rag_results": final_state["rag_results"],
        "agent_mode": "langgraph_nine_node",
        "state": final_state
    }
