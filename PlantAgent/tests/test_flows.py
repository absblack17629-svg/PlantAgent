# -*- coding: utf-8 -*-
"""
Flow 测试

测试流程编排功能。
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.flows import (
    BaseFlow,
    DetectionFlow,
    create_detection_flow,
    KnowledgeFlow,
    create_knowledge_flow
)
from services.agents.detection_agent import DetectionAgent
from services.agents.knowledge_agent import KnowledgeAgent
from services.exceptions import FlowError, AgentNotFoundError
from utils.logger import get_logger

logger = get_logger(__name__)


# ==================== BaseFlow 测试 ====================

def test_base_flow_agent_management():
    """测试 BaseFlow 的 Agent 管理功能"""
    print("\n" + "="*60)
    print("测试: BaseFlow Agent 管理")
    print("="*60)
    
    try:
        # 创建一个简单的 Flow 子类用于测试
        class TestFlow(BaseFlow):
            async def execute(self, input_data):
                return {"result": "test"}
        
        # 创建 Flow
        flow = TestFlow(name="test_flow", description="测试流程")
        print(f"✓ 创建 Flow: {flow}")
        
        # 创建 Agent
        agent1 = DetectionAgent(name="agent1")
        agent2 = KnowledgeAgent(name="agent2")
        
        # 添加 Agent
        flow.add_agent("detection", agent1)
        flow.add_agent("knowledge", agent2)
        print(f"✓ 添加 Agent: {flow.list_agents()}")
        
        # 获取 Agent
        retrieved_agent = flow.get_agent("detection")
        assert retrieved_agent is not None
        assert retrieved_agent.name == "agent1"
        print(f"✓ 获取 Agent: {retrieved_agent.name}")
        
        # 主 Agent
        primary = flow.primary_agent
        assert primary is not None
        assert primary.name == "agent1"  # 第一个添加的
        print(f"✓ 主 Agent: {primary.name}")
        
        # 设置主 Agent
        flow.set_primary_agent("knowledge")
        assert flow.primary_agent.name == "agent2"
        print(f"✓ 设置主 Agent: {flow.primary_agent.name}")
        
        # 移除 Agent
        removed = flow.remove_agent("detection")
        assert removed is True
        assert flow.get_agent("detection") is None
        print(f"✓ 移除 Agent: detection")
        
        # 列出 Agent
        agents = flow.list_agents()
        assert len(agents) == 1
        assert "knowledge" in agents
        print(f"✓ 列出 Agent: {agents}")
        
        print("\n✅ BaseFlow Agent 管理测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ BaseFlow Agent 管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_base_flow_require_agent():
    """测试 BaseFlow 的 require_agent 方法"""
    print("\n" + "="*60)
    print("测试: BaseFlow require_agent")
    print("="*60)
    
    try:
        class TestFlow(BaseFlow):
            async def execute(self, input_data):
                return {"result": "test"}
        
        flow = TestFlow(name="test_flow")
        agent = DetectionAgent(name="test_agent")
        flow.add_agent("test", agent)
        
        # 成功获取
        retrieved = flow.require_agent("test")
        assert retrieved is not None
        print(f"✓ require_agent 成功: {retrieved.name}")
        
        # 失败获取（应该抛出异常）
        try:
            flow.require_agent("nonexistent")
            print("❌ 应该抛出 AgentNotFoundError")
            return False
        except AgentNotFoundError as e:
            print(f"✓ 正确抛出异常: {e.error_code}")
        
        print("\n✅ BaseFlow require_agent 测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ BaseFlow require_agent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== DetectionFlow 测试 ====================

def test_detection_flow_creation():
    """测试 DetectionFlow 创建"""
    print("\n" + "="*60)
    print("测试: DetectionFlow 创建")
    print("="*60)
    
    try:
        # 使用构造函数创建
        flow1 = DetectionFlow()
        print(f"✓ 创建 DetectionFlow: {flow1}")
        
        # 检查 Agent
        assert "detection" in flow1.agents
        assert "knowledge" in flow1.agents
        print(f"✓ Agent 已设置: {flow1.list_agents()}")
        
        # 检查主 Agent
        assert flow1.primary_agent_key == "detection"
        print(f"✓ 主 Agent: {flow1.primary_agent_key}")
        
        # 使用工厂函数创建
        flow2 = create_detection_flow(
            confidence_threshold=0.6,
            auto_query_knowledge=False
        )
        assert flow2.confidence_threshold == 0.6
        assert flow2.auto_query_knowledge is False
        print(f"✓ 工厂函数创建: {flow2}")
        
        print("\n✅ DetectionFlow 创建测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ DetectionFlow 创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_detection_flow_execute():
    """测试 DetectionFlow 执行"""
    print("\n" + "="*60)
    print("测试: DetectionFlow 执行")
    print("="*60)
    
    try:
        flow = create_detection_flow(auto_query_knowledge=False)
        
        # 测试缺少参数
        try:
            await flow.execute({})
            print("❌ 应该抛出 FlowError")
            return False
        except FlowError as e:
            print(f"✓ 正确抛出异常: {e.error_code}")
        
        # 测试文件不存在
        try:
            await flow.execute({"image_path": "nonexistent.jpg"})
            print("❌ 应该抛出 FlowError")
            return False
        except FlowError as e:
            print(f"✓ 正确抛出异常: {e.error_code}")
        
        # 注意：实际执行需要真实的图像文件和模型
        # 这里只测试流程逻辑
        print("✓ 流程逻辑验证通过")
        
        print("\n✅ DetectionFlow 执行测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ DetectionFlow 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detection_flow_configuration():
    """测试 DetectionFlow 配置"""
    print("\n" + "="*60)
    print("测试: DetectionFlow 配置")
    print("="*60)
    
    try:
        flow = create_detection_flow()
        
        # 设置置信度阈值
        flow.set_confidence_threshold(0.7)
        assert flow.confidence_threshold == 0.7
        print(f"✓ 设置置信度阈值: {flow.confidence_threshold}")
        
        # 设置自动查询知识
        flow.set_auto_query_knowledge(False)
        assert flow.auto_query_knowledge is False
        print(f"✓ 设置自动查询: {flow.auto_query_knowledge}")
        
        print("\n✅ DetectionFlow 配置测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ DetectionFlow 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== KnowledgeFlow 测试 ====================

def test_knowledge_flow_creation():
    """测试 KnowledgeFlow 创建"""
    print("\n" + "="*60)
    print("测试: KnowledgeFlow 创建")
    print("="*60)
    
    try:
        # 使用构造函数创建
        flow1 = KnowledgeFlow()
        print(f"✓ 创建 KnowledgeFlow: {flow1}")
        
        # 检查 Agent
        assert "knowledge" in flow1.agents
        print(f"✓ Agent 已设置: {flow1.list_agents()}")
        
        # 检查主 Agent
        assert flow1.primary_agent_key == "knowledge"
        print(f"✓ 主 Agent: {flow1.primary_agent_key}")
        
        # 使用工厂函数创建
        flow2 = create_knowledge_flow(top_k=10, min_relevance=0.5)
        assert flow2.top_k == 10
        assert flow2.min_relevance == 0.5
        print(f"✓ 工厂函数创建: {flow2}")
        
        print("\n✅ KnowledgeFlow 创建测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ KnowledgeFlow 创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_flow_execute():
    """测试 KnowledgeFlow 执行"""
    print("\n" + "="*60)
    print("测试: KnowledgeFlow 执行")
    print("="*60)
    
    try:
        flow = create_knowledge_flow()
        
        # 测试缺少参数
        try:
            await flow.execute({})
            print("❌ 应该抛出 FlowError")
            return False
        except FlowError as e:
            print(f"✓ 正确抛出异常: {e.error_code}")
        
        # 注意：实际执行需要 RAG 服务
        # 这里只测试流程逻辑
        print("✓ 流程逻辑验证通过")
        
        print("\n✅ KnowledgeFlow 执行测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ KnowledgeFlow 执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_knowledge_flow_configuration():
    """测试 KnowledgeFlow 配置"""
    print("\n" + "="*60)
    print("测试: KnowledgeFlow 配置")
    print("="*60)
    
    try:
        flow = create_knowledge_flow()
        
        # 设置 top_k
        flow.set_top_k(10)
        assert flow.top_k == 10
        print(f"✓ 设置 top_k: {flow.top_k}")
        
        # 设置最小相关度
        flow.set_min_relevance(0.5)
        assert flow.min_relevance == 0.5
        print(f"✓ 设置最小相关度: {flow.min_relevance}")
        
        # 测试无效值
        try:
            flow.set_min_relevance(1.5)
            print("❌ 应该抛出 ValueError")
            return False
        except ValueError:
            print("✓ 正确拒绝无效值")
        
        print("\n✅ KnowledgeFlow 配置测试通过")
        return True
    
    except Exception as e:
        print(f"\n❌ KnowledgeFlow 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==================== 主测试函数 ====================

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始 Flow 测试")
    print("="*60)
    
    results = []
    
    # BaseFlow 测试
    results.append(("BaseFlow Agent 管理", test_base_flow_agent_management()))
    results.append(("BaseFlow require_agent", test_base_flow_require_agent()))
    
    # DetectionFlow 测试
    results.append(("DetectionFlow 创建", test_detection_flow_creation()))
    results.append(("DetectionFlow 执行", await test_detection_flow_execute()))
    results.append(("DetectionFlow 配置", test_detection_flow_configuration()))
    
    # KnowledgeFlow 测试
    results.append(("KnowledgeFlow 创建", test_knowledge_flow_creation()))
    results.append(("KnowledgeFlow 执行", await test_knowledge_flow_execute()))
    results.append(("KnowledgeFlow 配置", test_knowledge_flow_configuration()))
    
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
