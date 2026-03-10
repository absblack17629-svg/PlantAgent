# -*- coding: utf-8 -*-
"""
Flow 简单测试

测试流程编排的基础功能（不依赖外部服务）。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接导入 base 模块，避免触发其他依赖
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "flows"))
from base import BaseFlow

from services.agents.base import BaseAgent
from schemas.agent import AgentRole, AgentState
from services.exceptions import FlowError, AgentNotFoundError
from utils.logger import get_logger

logger = get_logger(__name__)


# ==================== 测试用的简单 Agent ====================

class SimpleAgent(BaseAgent):
    """简单的测试 Agent"""
    
    def __init__(self, **kwargs):
        if "name" not in kwargs:
            kwargs["name"] = "simple_agent"
        if "role" not in kwargs:
            kwargs["role"] = AgentRole.GENERAL
        super().__init__(**kwargs)
    
    async def step(self) -> str:
        """执行简单步骤"""
        self.mark_finished()
        return "步骤完成"


# ==================== 测试用的简单 Flow ====================

class SimpleFlow(BaseFlow):
    """简单的测试 Flow"""
    
    async def execute(self, input_data):
        """执行简单流程"""
        agent = self.require_agent("test")
        result = await agent.run("测试请求")
        return {"result": result}


# ==================== BaseFlow 测试 ====================

def test_base_flow_creation():
    """测试 BaseFlow 创建"""
    print("\n" + "="*60)
    print("测试 1: BaseFlow 创建")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow", description="测试流程")
        
        assert flow.name == "test_flow"
        assert flow.description == "测试流程"
        assert len(flow.agents) == 0
        assert flow.primary_agent_key is None
        
        print(f"✓ Flow 创建成功: {flow}")
        print(f"✓ 名称: {flow.name}")
        print(f"✓ 描述: {flow.description}")
        print(f"✓ Agent 数量: {len(flow.agents)}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_add_agent():
    """测试添加 Agent"""
    print("\n" + "="*60)
    print("测试 2: 添加 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent1 = SimpleAgent(name="agent1")
        agent2 = SimpleAgent(name="agent2")
        
        # 添加第一个 Agent
        flow.add_agent("test1", agent1)
        assert len(flow.agents) == 1
        assert "test1" in flow.agents
        assert flow.primary_agent_key == "test1"  # 第一个自动成为主 Agent
        print(f"✓ 添加 agent1: {flow.list_agents()}")
        
        # 添加第二个 Agent
        flow.add_agent("test2", agent2)
        assert len(flow.agents) == 2
        assert "test2" in flow.agents
        assert flow.primary_agent_key == "test1"  # 主 Agent 不变
        print(f"✓ 添加 agent2: {flow.list_agents()}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_get_agent():
    """测试获取 Agent"""
    print("\n" + "="*60)
    print("测试 3: 获取 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent = SimpleAgent(name="test_agent")
        flow.add_agent("test", agent)
        
        # 成功获取
        retrieved = flow.get_agent("test")
        assert retrieved is not None
        assert retrieved.name == "test_agent"
        print(f"✓ get_agent 成功: {retrieved.name}")
        
        # 获取不存在的 Agent
        none_agent = flow.get_agent("nonexistent")
        assert none_agent is None
        print(f"✓ get_agent 返回 None（不存在）")
        
        # require_agent 成功
        required = flow.require_agent("test")
        assert required is not None
        print(f"✓ require_agent 成功: {required.name}")
        
        # require_agent 失败
        try:
            flow.require_agent("nonexistent")
            print("❌ 应该抛出 AgentNotFoundError")
            return False
        except AgentNotFoundError as e:
            print(f"✓ require_agent 正确抛出异常: {e.error_code}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_primary_agent():
    """测试主 Agent"""
    print("\n" + "="*60)
    print("测试 4: 主 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent1 = SimpleAgent(name="agent1")
        agent2 = SimpleAgent(name="agent2")
        
        # 初始状态
        assert flow.primary_agent is None
        print(f"✓ 初始主 Agent: None")
        
        # 添加 Agent
        flow.add_agent("test1", agent1)
        assert flow.primary_agent.name == "agent1"
        print(f"✓ 添加后主 Agent: {flow.primary_agent.name}")
        
        # 添加第二个 Agent
        flow.add_agent("test2", agent2)
        assert flow.primary_agent.name == "agent1"  # 不变
        print(f"✓ 添加第二个后主 Agent: {flow.primary_agent.name}")
        
        # 设置主 Agent
        flow.set_primary_agent("test2")
        assert flow.primary_agent.name == "agent2"
        print(f"✓ 设置后主 Agent: {flow.primary_agent.name}")
        
        # 设置不存在的主 Agent
        try:
            flow.set_primary_agent("nonexistent")
            print("❌ 应该抛出 AgentNotFoundError")
            return False
        except AgentNotFoundError:
            print(f"✓ 正确拒绝不存在的 Agent")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_remove_agent():
    """测试移除 Agent"""
    print("\n" + "="*60)
    print("测试 5: 移除 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent1 = SimpleAgent(name="agent1")
        agent2 = SimpleAgent(name="agent2")
        
        flow.add_agent("test1", agent1)
        flow.add_agent("test2", agent2)
        assert len(flow.agents) == 2
        print(f"✓ 初始 Agent: {flow.list_agents()}")
        
        # 移除存在的 Agent
        removed = flow.remove_agent("test1")
        assert removed is True
        assert len(flow.agents) == 1
        assert "test1" not in flow.agents
        print(f"✓ 移除 test1: {flow.list_agents()}")
        
        # 移除不存在的 Agent
        removed = flow.remove_agent("nonexistent")
        assert removed is False
        print(f"✓ 移除不存在的 Agent 返回 False")
        
        # 移除主 Agent
        flow.set_primary_agent("test2")
        flow.remove_agent("test2")
        assert flow.primary_agent_key is None
        print(f"✓ 移除主 Agent 后 primary_agent_key: None")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_list_agents():
    """测试列出 Agent"""
    print("\n" + "="*60)
    print("测试 6: 列出 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        
        # 空列表
        agents = flow.list_agents()
        assert len(agents) == 0
        print(f"✓ 初始列表: {agents}")
        
        # 添加 Agent
        agent1 = SimpleAgent(name="agent1")
        agent2 = SimpleAgent(name="agent2")
        flow.add_agent("test1", agent1)
        flow.add_agent("test2", agent2)
        
        agents = flow.list_agents()
        assert len(agents) == 2
        assert agents["test1"] == "agent1"
        assert agents["test2"] == "agent2"
        print(f"✓ Agent 列表: {agents}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_base_flow_execute():
    """测试执行流程"""
    print("\n" + "="*60)
    print("测试 7: 执行流程")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent = SimpleAgent(name="test_agent")
        flow.add_agent("test", agent)
        
        # 执行流程
        result = await flow.execute({"input": "test"})
        assert result is not None
        assert "result" in result
        print(f"✓ 执行结果: {result}")
        
        # 使用 run 方法（带错误处理）
        result2 = await flow.run({"input": "test2"})
        assert result2 is not None
        print(f"✓ run 方法结果: {result2}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_reset_agents():
    """测试重置 Agent"""
    print("\n" + "="*60)
    print("测试 8: 重置 Agent")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent1 = SimpleAgent(name="agent1")
        agent2 = SimpleAgent(name="agent2")
        
        flow.add_agent("test1", agent1)
        flow.add_agent("test2", agent2)
        
        # 修改 Agent 状态
        agent1.state = AgentState.RUNNING
        agent2.state = AgentState.FINISHED
        agent1.current_step = 5
        agent2.current_step = 10
        
        print(f"✓ 修改前状态: agent1={agent1.state.value}, agent2={agent2.state.value}")
        print(f"✓ 修改前步骤: agent1={agent1.current_step}, agent2={agent2.current_step}")
        
        # 重置所有 Agent
        flow.reset_agents()
        
        assert agent1.state == AgentState.IDLE
        assert agent2.state == AgentState.IDLE
        assert agent1.current_step == 0
        assert agent2.current_step == 0
        
        print(f"✓ 重置后状态: agent1={agent1.state.value}, agent2={agent2.state.value}")
        print(f"✓ 重置后步骤: agent1={agent1.current_step}, agent2={agent2.current_step}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_to_dict():
    """测试转换为字典"""
    print("\n" + "="*60)
    print("测试 9: 转换为字典")
    print("="*60)
    
    try:
        flow = SimpleFlow(
            name="test_flow",
            description="测试流程",
            metadata={"version": "1.0"}
        )
        agent = SimpleAgent(name="test_agent")
        flow.add_agent("test", agent)
        
        # 转换为字典
        flow_dict = flow.to_dict()
        
        assert flow_dict["name"] == "test_flow"
        assert flow_dict["description"] == "测试流程"
        assert "test" in flow_dict["agents"]
        assert flow_dict["primary_agent"] == "test"
        assert flow_dict["metadata"]["version"] == "1.0"
        
        print(f"✓ Flow 字典: {flow_dict}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_str_repr():
    """测试字符串表示"""
    print("\n" + "="*60)
    print("测试 10: 字符串表示")
    print("="*60)
    
    try:
        flow = SimpleFlow(name="test_flow")
        agent = SimpleAgent(name="test_agent")
        flow.add_agent("test", agent)
        
        # __str__
        str_repr = str(flow)
        assert "test_flow" in str_repr
        assert "1" in str_repr  # 1 agent
        print(f"✓ __str__: {str_repr}")
        
        # __repr__
        repr_str = repr(flow)
        assert "SimpleFlow" in repr_str
        assert "test_flow" in repr_str
        print(f"✓ __repr__: {repr_str}")
        
        print("\n✅ 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== 主测试函数 ====================

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始 Flow 简单测试")
    print("="*60)
    
    results = []
    
    # 同步测试
    results.append(("BaseFlow 创建", test_base_flow_creation()))
    results.append(("添加 Agent", test_base_flow_add_agent()))
    results.append(("获取 Agent", test_base_flow_get_agent()))
    results.append(("主 Agent", test_base_flow_primary_agent()))
    results.append(("移除 Agent", test_base_flow_remove_agent()))
    results.append(("列出 Agent", test_base_flow_list_agents()))
    results.append(("重置 Agent", test_base_flow_reset_agents()))
    results.append(("转换为字典", test_base_flow_to_dict()))
    results.append(("字符串表示", test_base_flow_str_repr()))
    
    # 异步测试
    results.append(("执行流程", await test_base_flow_execute()))
    
    # 统计结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
