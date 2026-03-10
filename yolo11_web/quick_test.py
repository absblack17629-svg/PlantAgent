# -*- coding: utf-8 -*-
"""快速测试Agent"""
import requests
import json

def test_question(question):
    """测试单个问题"""
    print(f"\n{'='*60}")
    print(f"📝 问题: {question}")
    print(f"{'='*60}")
    
    try:
        # 注意：路由是 /api/agent/chat，且使用 Form 数据
        response = requests.post(
            "http://localhost:8000/api/agent/chat",
            data={"message": question},  # 使用 Form 数据，字段名是 message
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print(f"\n✅ 成功")
                response_data = data.get('data', {})
                print(f"\n💬 回复:\n{response_data.get('response', '无回复')}")
                print(f"\n🤖 模式: {response_data.get('agent_mode', 'unknown')}")
                tools = response_data.get('tools_used', [])
                if tools:
                    print(f"🔧 使用工具: {', '.join(tools)}")
            else:
                print(f"\n❌ 失败: {data.get('msg')}")
        else:
            print(f"\n❌ HTTP {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")

# 测试3个问题
print("🤖 开始测试智谱AI Agent")

test_question("你好，请介绍一下你自己")
test_question("水稻常见的病害有哪些？")
test_question("帮我制定一个水稻病害检测的工作计划")

print(f"\n{'='*60}")
print("✅ 测试完成")
print(f"{'='*60}")
