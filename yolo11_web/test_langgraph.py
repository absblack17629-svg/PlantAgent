# -*- coding: utf-8 -*-
"""LangGraph 客服工作流测试"""

import sys
import os

os.chdir(r"C:\Users\1\Desktop\file\Fastapi_backend\yolo11_web")

print("=" * 50)
print("LangGraph 客服工作流测试")
print("=" * 50)

# 1. 测试 LangGraph 导入
print("\n[1] LangGraph 导入...")
try:
    from langgraph.graph import StateGraph, END
    from langgraph.graph.message import add_messages

    print("    OK - LangGraph 导入成功")
except Exception as e:
    print(f"    FAIL - {e}")

# 2. 测试状态定义
print("\n[2] 九节点状态定义...")
try:
    from yoloapp.flow.nine_node_graph import NineNodeState

    state = NineNodeState(
        user_input="test",
        image_path=None,
        messages=[],
        intent="chat",
        emotion="neutral",
        confidence=0.8,
        context="test",
        input_validation={},
        tool_plan=[],
        tool_results=[],
        rag_results=[],
        response="",
        metadata={},
    )
    print("    OK - 状态定义正常")
except Exception as e:
    print(f"    FAIL - {e}")

# 3. 测试工作流创建
print("\n[3] 创建工作流...")
try:
    from yoloapp.flow.nine_node_graph import create_nine_node_graph

    app = create_nine_node_graph()
    print("    OK - 工作流创建成功")
except Exception as e:
    print(f"    FAIL - {e}")

# 4. 测试 Agent 导入
print("\n[4] 导入9个Agent...")
try:
    from yoloapp.agent import (
        IntentAgent,
        ContextAgent,
        MemoryAgent,
        PlanningAgent,
        InputValidationAgent,
        ToolExecutionAgent,
        ResultValidationAgent,
        RAGAgent,
        ResponseAgent,
    )

    print("    OK - 9个Agent导入成功")
    print("      - IntentAgent (意图识别)")
    print("      - ContextAgent (上下文管理)")
    print("      - MemoryAgent (记忆管理)")
    print("      - PlanningAgent (工具规划)")
    print("      - InputValidationAgent (输入验证)")
    print("      - ToolExecutionAgent (工具执行)")
    print("      - ResultValidationAgent (结果验证)")
    print("      - RAGAgent (知识检索)")
    print("      - ResponseAgent (响应生成)")
except Exception as e:
    print(f"    FAIL - {e}")

# 5. 测试 LangGraph API 路由
print("\n[5] API路由导入...")
try:
    from routers.langgraph_api import router

    print(f"    OK - LangGraph API 路由 ({len(router.routes)} 个端点)")
except Exception as e:
    print(f"    FAIL - {e}")

# 6. 测试 agent_factory
print("\n[6] Agent Factory...")
try:
    from routers.agent_factory import process_agent_request

    print("    OK - process_agent_request 可用")
except Exception as e:
    print(f"    FAIL - {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)
print("\n注: 完整功能测试需要:")
print("  1. MySQL 数据库运行中")
print("  2. Redis 服务运行中")
print("  3. LLM API Key 已配置")
print("\n可通过 http://localhost:8000/docs 进行API测试")
