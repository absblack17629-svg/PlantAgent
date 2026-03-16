# -*- coding: utf-8 -*-
"""
LLM 服务测试
"""

import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm.token_counter import TokenCounter
from services.llm.client import LLMClient, get_llm_client
from schemas.message import Message


async def test_token_counter():
    """测试 Token 计数器"""
    print("\n[TEST] Token 计数器")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        print(f"[OK] 创建 Token 计数器")
        
        # 测试文本计数
        text = "Hello, world! 你好，世界！"
        tokens = counter.count_text(text)
        print(f"[OK] 文本 Token 数: {tokens}")
        
        # 测试消息计数
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        tokens = counter.count_messages(messages)
        print(f"[OK] 消息 Token 数: {tokens}")
        
        # 测试 token 限制检查
        is_within, current = counter.check_limit(messages, max_tokens=1000)
        print(f"[OK] Token 限制检查: {is_within}, 当前: {current}")
        
        # 测试消息截断
        long_messages = messages * 10
        truncated = counter.truncate_messages(long_messages, max_tokens=500)
        print(f"[OK] 消息截断: {len(long_messages)} -> {len(truncated)}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_client_init():
    """测试 LLM 客户端初始化"""
    print("\n[TEST] LLM 客户端初始化")
    
    try:
        # 测试默认配置
        client = get_llm_client("default")
        print(f"[OK] 创建默认客户端: {client}")
        
        # 测试单例模式
        client2 = get_llm_client("default")
        assert client is client2
        print(f"[OK] 单例模式正确")
        
        # 测试多配置
        client_zhipu = get_llm_client("zhipu")
        print(f"[OK] 创建智谱客户端: {client_zhipu}")
        
        # 测试统计信息
        stats = client.get_token_stats()
        print(f"[OK] 获取统计信息: {stats['model']}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_llm_client_format():
    """测试消息格式化"""
    print("\n[TEST] 消息格式化")
    
    try:
        client = get_llm_client("default")
        
        # 测试 Message 对象
        messages = [
            Message.system_message("You are a helpful assistant."),
            Message.user_message("Hello!"),
        ]
        
        formatted = client._format_messages(messages)
        assert len(formatted) == 2
        assert formatted[0]["role"] == "system"
        print(f"[OK] Message 对象格式化正确")
        
        # 测试字典
        dict_messages = [
            {"role": "user", "content": "Test"}
        ]
        
        formatted = client._format_messages(dict_messages)
        assert len(formatted) == 1
        print(f"[OK] 字典格式化正确")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_reset():
    """测试 Token 重置"""
    print("\n[TEST] Token 重置")
    
    try:
        client = get_llm_client("default")
        
        # 设置一些 token
        client.total_tokens = 1000
        print(f"[OK] 设置 Token: {client.total_tokens}")
        
        # 重置
        client.reset_token_count()
        assert client.total_tokens == 0
        print(f"[OK] Token 重置成功: {client.total_tokens}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def run_tests():
    """运行测试"""
    print("=" * 60)
    print("LLM 服务测试")
    print("=" * 60)
    
    tests = [
        ("Token 计数器", test_token_counter),
        ("LLM 客户端初始化", test_llm_client_init),
        ("消息格式化", test_llm_client_format),
        ("Token 重置", test_token_reset),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    exit(0 if success else 1)
