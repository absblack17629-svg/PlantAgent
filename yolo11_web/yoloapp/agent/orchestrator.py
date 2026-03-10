# -*- coding: utf-8 -*-
"""
九节点工作流编排器
负责协调九个 Agent 的执行流程
"""

from typing import Dict, List, Any, Optional, Callable
from yoloapp.schema import Memory, Message
from yoloapp.exceptions import AgentError, FlowError
from yoloapp.utils.logger import get_logger

# 导入九个节点 Agent
from .intent_agent import IntentAgent
from .context_agent import ContextAgent
from .memory_agent import MemoryAgent
from .planning_agent import PlanningAgent
from .input_validation_agent import InputValidationAgent
from .tool_execution_agent import ToolExecutionAgent
from .result_validation_agent import ResultValidationAgent
from .rag_agent import RAGAgent
from .response_agent import ResponseAgent

logger = get_logger(__name__)


class NineNodeOrchestrator:
    """
    九节点工作流编排器
    
    流程:
    1. IntentAgent - 意图理解 + 情感分析
    2. ContextAgent - 上下文管理
    3. MemoryAgent - 对话记忆
    4. PlanningAgent - 工具规划
    5. InputValidationAgent - 输入验证
    6. ToolExecutionAgent - 工具执行
    7. ResultValidationAgent - 结果验证
    8. RAGAgent - RAG检索
    9. ResponseAgent - 响应生成
    
    特性:
    - 统一的 Memory 管理
    - 流式处理支持
    - 错误处理和恢复
    """
    
    def __init__(
        self,
        skill_client=None,
        stream_callback: Optional[Callable] = None
    ):
        """
        初始化编排器
        
        Args:
            skill_client: 技能客户端
            stream_callback: 流式回调函数
        """
        self.skill_client = skill_client
        self.stream_callback = stream_callback
        
        # 创建共享的 Memory
        self.memory = Memory()
        
        # 创建九个 Agent 实例
        self.agents = self._create_agents()
        
        # 定义处理流程
        self.pipeline = [
            "intent",
            "context",
            "memory",
            "planning",
            "input_validation",
            "tool_execution",
            "result_validation",
            "rag",
            "response"
        ]
        
        logger.info(f"[OK] NineNodeOrchestrator 初始化完成，包含 {len(self.agents)} 个Agent")
    
    def _create_agents(self) -> Dict[str, Any]:
        """创建所有 Agent 实例"""
        agents = {
            "intent": IntentAgent(),
            "context": ContextAgent(self.skill_client),
            "memory": MemoryAgent(self.skill_client),
            "planning": PlanningAgent(),
            "input_validation": InputValidationAgent(),
            "tool_execution": ToolExecutionAgent(self.skill_client),
            "result_validation": ResultValidationAgent(),
            "rag": RAGAgent(self.skill_client),
            "response": ResponseAgent()
        }
        
        # 为所有 Agent 设置共享的 Memory
        for agent in agents.values():
            agent.memory = self.memory
        
        return agents
    
    async def process(
        self,
        user_input: str,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入文本
            image_path: 图片路径（可选）
            
        Returns:
            包含响应和处理信息的字典
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"🚀 开始九节点工作流处理")
            logger.info(f"{'='*60}")
            logger.info(f"用户输入: {user_input[:50]}...")
            logger.info(f"图片路径: {image_path}")
            
            # 1. 初始化 Memory
            self.memory.clear()
            self.memory.add_message(Message(role="user", content=user_input))
            self.memory.metadata["image_path"] = image_path
            
            # 2. 先执行意图识别
            intent_agent = self.agents["intent"]
            logger.info(f"\n[intent] 开始处理...")
            await intent_agent.step()
            logger.info(f"[intent] 完成")
            
            intent = self.memory.metadata.get("intent", "chat")
            logger.info(f"📋 识别意图: {intent}")
            
            # 3. 判断是否需要完整流程
            if intent in ["greet", "goodbye", "chat"]:
                # 普通对话：直接使用 LLM 快速响应
                logger.info(f"⚡ 检测到普通对话意图，使用快速通道...")
                
                # 直接调用 ResponseAgent 生成回复
                response_agent = self.agents["response"]
                response = await response_agent.step()
                
                if self.stream_callback:
                    self._emit_stream("response", response)
                
                logger.info(f"[OK] 快速通道处理完成")
            
            else:
                # 检测/查询意图：执行完整的九节点流程
                logger.info(f"🔧 检测到专业任务意图，执行完整流程...")
                
                # 从 context 开始执行剩余节点
                remaining_pipeline = self.pipeline[1:]  # 跳过 intent
                
                for agent_name in remaining_pipeline:
                    agent = self.agents[agent_name]
                    
                    logger.info(f"\n[{agent_name}] 开始处理...")
                    
                    try:
                        # 执行 Agent
                        result = await agent.step()
                        
                        # 发射流式事件
                        if self.stream_callback:
                            self._emit_stream(agent_name, result)
                        
                        logger.info(f"[{agent_name}] 完成")
                        
                        # 输入验证后检查是否需要澄清
                        if agent_name == "input_validation":
                            input_validation = self.memory.metadata.get("input_validation", {})
                            if input_validation.get("clarification_needed"):
                                logger.info(f"[WARN] 输入验证失败，需要澄清，跳转到响应生成...")
                                # 直接跳到响应生成
                                response_agent = self.agents["response"]
                                response = await response_agent.step()
                                if self.stream_callback:
                                    self._emit_stream("response", response)
                                break
                    
                    except Exception as e:
                        logger.error(f"[{agent_name}] 执行失败: {e}")
                        # 继续执行下一个节点，不中断流程
                        continue
            
            # 3. 获取最终响应
            response = self.memory.metadata.get("response", "处理完成")
            
            logger.info(f"\n{'='*60}")
            logger.info(f"[OK] 九节点工作流处理完成")
            logger.info(f"{'='*60}")
            
            # 4. 返回结果
            return {
                "success": True,
                "response": response,
                "intent": self.memory.metadata.get("intent"),
                "emotion": self.memory.metadata.get("emotion"),
                "tool_results": self.memory.metadata.get("tool_results", []),
                "agent_mode": "nine_node_openmanus_style",
                "memory": {
                    "messages": [msg.model_dump() for msg in self.memory.messages],
                    "metadata": self.memory.metadata
                }
            }
            
        except Exception as e:
            error_msg = f"工作流执行失败: {str(e)}"
            logger.error(error_msg)
            raise FlowError(error_msg)
    
    def _emit_stream(self, agent_name: str, result: str):
        """发射流式事件"""
        if self.stream_callback:
            try:
                self.stream_callback({
                    "agent": agent_name,
                    "result": result
                })
            except Exception as e:
                logger.warning(f"流式回调失败: {e}")


def create_nine_node_orchestrator(
    skill_client=None,
    stream_callback: Optional[Callable] = None
) -> NineNodeOrchestrator:
    """
    创建九节点编排器实例
    
    Args:
        skill_client: 技能客户端
        stream_callback: 流式回调函数
        
    Returns:
        NineNodeOrchestrator 实例
    """
    return NineNodeOrchestrator(skill_client, stream_callback)
