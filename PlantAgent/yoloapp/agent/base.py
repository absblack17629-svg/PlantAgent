# -*- coding: utf-8 -*-
"""
Agent 基类

提供所有 Agent 的基础功能，包括状态管理、记忆管理和执行循环。
"""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

from yoloapp.schema import AgentRole, AgentState, AgentConfig, Message, Memory
from yoloapp.exceptions import AgentError, AgentStateError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(BaseModel, ABC):
    """Agent 基类
    
    提供 Agent 的基础功能，包括：
    - 状态管理（IDLE, RUNNING, FINISHED, ERROR）
    - 记忆管理（Memory）
    - 执行循环（run 方法）
    - 卡住检测（is_stuck 方法）
    
    子类需要实现：
    - step() 方法：定义单步执行逻辑
    
    Attributes:
        name: Agent 名称
        role: Agent 角色
        description: Agent 描述
        state: 当前状态
        memory: 消息记忆
        max_steps: 最大执行步骤数
        current_step: 当前步骤数
        duplicate_threshold: 重复检测阈值
        llm_config: LLM 配置
        metadata: 额外元数据
    """
    
    # 核心属性
    name: str = Field(..., description="Agent 名称")
    role: AgentRole = Field(default=AgentRole.GENERAL, description="Agent 角色")
    description: Optional[str] = Field(None, description="Agent 描述")
    
    # 状态管理
    state: AgentState = Field(default=AgentState.IDLE, description="当前状态")
    memory: Memory = Field(default_factory=Memory, description="消息记忆")
    
    # 执行控制
    max_steps: int = Field(default=10, description="最大执行步骤数", ge=1, le=100)
    current_step: int = Field(default=0, description="当前步骤数", ge=0)
    duplicate_threshold: int = Field(default=2, description="重复检测阈值", ge=1)
    
    # 配置
    llm_config: Optional[Dict[str, Any]] = Field(None, description="LLM 配置")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # 允许额外字段，提供灵活性
    
    @model_validator(mode="after")
    def initialize_agent(self) -> "BaseAgent":
        """初始化 Agent
        
        在模型创建后自动调用，用于初始化默认值。
        
        Returns:
            初始化后的 Agent 实例
        """
        # 确保 memory 是 Memory 实例
        if not isinstance(self.memory, Memory):
            self.memory = Memory()
        
        # 设置默认描述
        if not self.description:
            self.description = f"{self.role.value} agent"
        
        logger.info(f"初始化 Agent: {self.name} (角色: {self.role.value})")
        return self
    
    @asynccontextmanager
    async def state_context(self, new_state: AgentState):
        """状态上下文管理器
        
        安全地管理状态转换，确保异常时状态正确恢复。
        
        Args:
            new_state: 要转换到的新状态
            
        Yields:
            None
            
        Raises:
            ValueError: 如果新状态无效
        
        Example:
            async with agent.state_context(AgentState.RUNNING):
                # 执行代码
                pass
        """
        if not isinstance(new_state, AgentState):
            raise ValueError(f"无效的状态: {new_state}")
        
        previous_state = self.state
        self.state = new_state
        logger.debug(f"Agent {self.name} 状态转换: {previous_state.value} -> {new_state.value}")
        
        try:
            yield
        except Exception as e:
            # 发生异常时转换到 ERROR 状态
            self.state = AgentState.ERROR
            logger.error(f"Agent {self.name} 执行出错: {e}")
            raise
        finally:
            # 如果不是 ERROR 状态，恢复到之前的状态
            if self.state != AgentState.ERROR:
                self.state = previous_state
    
    def update_memory(
        self,
        role: str,
        content: str,
        **kwargs
    ) -> None:
        """更新记忆
        
        添加消息到记忆中的便捷方法。
        
        Args:
            role: 消息角色（user, system, assistant）
            content: 消息内容
            **kwargs: 其他参数（如 metadata 等）
        
        Raises:
            ValueError: 如果角色不支持
        """
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
        }
        
        if role not in message_map:
            raise ValueError(f"不支持的消息角色: {role}，支持的角色: {list(message_map.keys())}")
        
        # 根据角色创建消息
        message = message_map[role](content, **kwargs)
        
        self.memory.add_message(message)
        logger.debug(f"Agent {self.name} 添加消息: [{role}] {content[:50]}...")
    
    async def run(self, request: Optional[str] = None) -> str:
        """执行 Agent 主循环
        
        这是 Agent 的主要执行方法，会循环调用 step() 直到完成或达到最大步骤数。
        
        Args:
            request: 可选的初始请求
            
        Returns:
            执行结果摘要
            
        Raises:
            AgentStateError: 如果 Agent 不在 IDLE 状态
            AgentError: 如果执行过程中发生错误
        
        Example:
            result = await agent.run("请检测这张图片")
        """
        # 检查状态
        if self.state != AgentState.IDLE:
            raise AgentStateError(
                agent_name=self.name,
                current_state=self.state.value,
                expected_state=AgentState.IDLE.value
            )
        
        # 添加初始请求
        if request:
            self.update_memory("user", request)
            logger.info(f"Agent {self.name} 收到请求: {request[:100]}...")
        
        results: List[str] = []
        
        # 使用状态上下文管理器
        async with self.state_context(AgentState.RUNNING):
            while self.current_step < self.max_steps and not self.is_finished():
                self.current_step += 1
                logger.info(f"Agent {self.name} 执行步骤 {self.current_step}/{self.max_steps}")
                
                try:
                    # 执行单步
                    step_result = await self.step()
                    results.append(f"步骤 {self.current_step}: {step_result}")
                    
                    # 检查是否卡住
                    if self.is_stuck():
                        logger.warning(f"Agent {self.name} 检测到卡住状态")
                        self.handle_stuck()
                
                except Exception as e:
                    error_msg = f"步骤 {self.current_step} 执行失败: {e}"
                    logger.error(f"Agent {self.name} {error_msg}")
                    results.append(error_msg)
                    raise AgentError(
                        message=error_msg,
                        error_code="STEP_EXECUTION_FAILED",
                        context={
                            "agent_name": self.name,
                            "step": self.current_step,
                            "error": str(e)
                        }
                    )
            
            # 检查是否达到最大步骤数
            if self.current_step >= self.max_steps:
                logger.warning(f"Agent {self.name} 达到最大步骤数 {self.max_steps}")
                results.append(f"已达到最大步骤数 ({self.max_steps})")
                self.current_step = 0  # 重置步骤计数
        
        # 生成结果摘要
        summary = "\n".join(results) if results else "未执行任何步骤"
        logger.info(f"Agent {self.name} 执行完成，共 {self.current_step} 步")
        
        return summary
    
    @abstractmethod
    async def step(self) -> str:
        """执行单步操作
        
        这是抽象方法，必须由子类实现。
        定义 Agent 的具体执行逻辑。
        
        Returns:
            步骤执行结果描述
            
        Raises:
            NotImplementedError: 如果子类未实现
        
        Example:
            async def step(self) -> str:
                # 执行检测
                result = await self.detect_image()
                return f"检测完成: {result}"
        """
        raise NotImplementedError("子类必须实现 step() 方法")
    
    def is_stuck(self) -> bool:
        """检测是否卡住
        
        通过检测最近的消息是否重复来判断 Agent 是否卡在循环中。
        
        Returns:
            是否卡住
        """
        if len(self.memory.messages) < self.duplicate_threshold + 1:
            return False
        
        # 获取最后一条消息
        last_message = self.memory.messages[-1]
        if not last_message.content or last_message.role != "assistant":
            return False
        
        # 统计重复次数
        duplicate_count = 0
        for msg in reversed(self.memory.messages[:-1]):
            if msg.role == "assistant" and msg.content == last_message.content:
                duplicate_count += 1
                if duplicate_count >= self.duplicate_threshold:
                    return True
        
        return False
    
    def handle_stuck(self) -> None:
        """处理卡住状态
        
        当检测到 Agent 卡住时，添加系统提示来改变策略。
        """
        stuck_prompt = (
            "检测到重复响应。请尝试新的策略，"
            "避免重复之前已经尝试过但无效的方法。"
        )
        self.update_memory("system", stuck_prompt)
        logger.warning(f"Agent {self.name} 添加卡住提示")
    
    def is_finished(self) -> bool:
        """判断是否完成
        
        Returns:
            是否处于 FINISHED 状态
        """
        return self.state == AgentState.FINISHED
    
    def mark_finished(self) -> None:
        """标记为完成状态"""
        self.state = AgentState.FINISHED
        logger.info(f"Agent {self.name} 标记为完成")
    
    def reset(self) -> None:
        """重置 Agent 状态
        
        清空记忆，重置步骤计数，恢复到 IDLE 状态。
        """
        self.memory.clear()
        self.current_step = 0
        self.state = AgentState.IDLE
        logger.info(f"Agent {self.name} 已重置")
    
    def get_config(self) -> AgentConfig:
        """获取 Agent 配置
        
        Returns:
            Agent 配置对象
        """
        return AgentConfig(
            name=self.name,
            role=self.role,
            description=self.description,
            max_steps=self.max_steps,
            llm_config=self.llm_config,
            metadata=self.metadata
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            字典格式的 Agent 信息
        """
        return {
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "state": self.state.value,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "message_count": self.memory.count(),
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} ({self.role.value}, {self.state.value})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name} "
            f"role={self.role.value} "
            f"state={self.state.value} "
            f"step={self.current_step}/{self.max_steps}>"
        )
