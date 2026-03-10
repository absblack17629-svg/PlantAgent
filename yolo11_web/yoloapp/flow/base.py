# -*- coding: utf-8 -*-
"""
Flow 基类

提供流程编排的基础功能。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from yoloapp.agent.base import BaseAgent
from yoloapp.exceptions import FlowError, AgentNotFoundError
from yoloapp.utils.logger import get_logger

logger = get_logger(__name__)


class BaseFlow(BaseModel, ABC):
    """Flow 基类
    
    提供流程编排的基础功能，包括：
    - Agent 管理
    - 流程执行
    - 错误处理
    
    子类需要实现：
    - execute() 方法：定义具体的流程逻辑
    
    Attributes:
        name: Flow 名称
        description: Flow 描述
        agents: Agent 字典
        primary_agent_key: 主 Agent 的 key
        metadata: 额外元数据
    """
    
    # 核心属性
    name: str = Field(..., description="Flow 名称")
    description: Optional[str] = Field(None, description="Flow 描述")
    
    # Agent 管理
    agents: Dict[str, BaseAgent] = Field(default_factory=dict, description="Agent 字典")
    primary_agent_key: Optional[str] = Field(None, description="主 Agent 的 key")
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"
    
    def add_agent(self, key: str, agent: BaseAgent) -> None:
        """添加 Agent
        
        Args:
            key: Agent 的唯一标识
            agent: Agent 实例
            
        Example:
            flow.add_agent("detection", detection_agent)
        """
        self.agents[key] = agent
        
        # 如果还没有主 Agent，将第一个添加的 Agent 设为主 Agent
        if not self.primary_agent_key:
            self.primary_agent_key = key
        
        logger.info(f"Flow {self.name} 添加 Agent: {key} ({agent.name})")
    
    def get_agent(self, key: str) -> Optional[BaseAgent]:
        """获取 Agent
        
        Args:
            key: Agent 的唯一标识
            
        Returns:
            Agent 实例，如果不存在返回 None
            
        Example:
            agent = flow.get_agent("detection")
        """
        agent = self.agents.get(key)
        
        if agent is None:
            logger.warning(f"Flow {self.name} 未找到 Agent: {key}")
        
        return agent
    
    def require_agent(self, key: str) -> BaseAgent:
        """获取 Agent（必须存在）
        
        Args:
            key: Agent 的唯一标识
            
        Returns:
            Agent 实例
            
        Raises:
            AgentNotFoundError: 如果 Agent 不存在
            
        Example:
            agent = flow.require_agent("detection")
        """
        agent = self.get_agent(key)
        
        if agent is None:
            raise AgentNotFoundError(
                agent_key=key,
                available_agents=list(self.agents.keys())
            )
        
        return agent
    
    @property
    def primary_agent(self) -> Optional[BaseAgent]:
        """获取主 Agent
        
        Returns:
            主 Agent 实例，如果不存在返回 None
        """
        if not self.primary_agent_key:
            return None
        
        return self.get_agent(self.primary_agent_key)
    
    def set_primary_agent(self, key: str) -> None:
        """设置主 Agent
        
        Args:
            key: Agent 的唯一标识
            
        Raises:
            AgentNotFoundError: 如果 Agent 不存在
        """
        if key not in self.agents:
            raise AgentNotFoundError(
                agent_key=key,
                available_agents=list(self.agents.keys())
            )
        
        self.primary_agent_key = key
        logger.info(f"Flow {self.name} 设置主 Agent: {key}")
    
    def remove_agent(self, key: str) -> bool:
        """移除 Agent
        
        Args:
            key: Agent 的唯一标识
            
        Returns:
            是否成功移除
        """
        if key in self.agents:
            del self.agents[key]
            
            # 如果移除的是主 Agent，清空主 Agent key
            if self.primary_agent_key == key:
                self.primary_agent_key = None
            
            logger.info(f"Flow {self.name} 移除 Agent: {key}")
            return True
        
        return False
    
    def list_agents(self) -> Dict[str, str]:
        """列出所有 Agent
        
        Returns:
            Agent key 到 Agent 名称的映射
        """
        return {key: agent.name for key, agent in self.agents.items()}
    
    @abstractmethod
    async def execute(self, input_data: Any) -> Any:
        """执行流程（子类实现）
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
            
        Raises:
            FlowError: 流程执行失败
            
        Example:
            async def execute(self, image_path: str) -> Dict:
                # 1. 执行检测
                detection_agent = self.require_agent("detection")
                detection_result = await detection_agent.run(f"检测图像: {image_path}")
                
                # 2. 执行知识查询
                knowledge_agent = self.require_agent("knowledge")
                advice = await knowledge_agent.run(f"提供建议: {detection_result}")
                
                return {
                    "detection": detection_result,
                    "advice": advice
                }
        """
        raise NotImplementedError("子类必须实现 execute() 方法")
    
    async def run(self, input_data: Any) -> Any:
        """运行流程（带错误处理）
        
        Args:
            input_data: 输入数据
            
        Returns:
            执行结果
            
        Raises:
            FlowError: 流程执行失败
        """
        try:
            logger.info(f"Flow {self.name} 开始执行")
            result = await self.execute(input_data)
            logger.info(f"Flow {self.name} 执行完成")
            return result
        
        except Exception as e:
            logger.error(f"Flow {self.name} 执行失败: {e}", exc_info=True)
            raise FlowError(
                message=f"Flow 执行失败: {str(e)}",
                error_code="FLOW_EXECUTION_FAILED",
                context={
                    "flow_name": self.name,
                    "error": str(e)
                }
            )
    
    def reset_agents(self) -> None:
        """重置所有 Agent"""
        for agent in self.agents.values():
            agent.reset()
        
        logger.info(f"Flow {self.name} 已重置所有 Agent")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典
        
        Returns:
            字典格式的 Flow 信息
        """
        return {
            "name": self.name,
            "description": self.description,
            "agents": self.list_agents(),
            "primary_agent": self.primary_agent_key,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} ({len(self.agents)} agents)"
    
    def __repr__(self) -> str:
        """详细表示"""
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name} "
            f"agents={len(self.agents)}>"
        )
