# -*- coding: utf-8 -*-
"""
LLM 服务简单测试（不依赖外部库）
"""

import asyncio
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm.token_counter import TokenCounter
from schemas.message import Message


async def test_token_counter_basic():
    """测试 Token 计数器基础功能"""
    print("\n[TEST] Token 计数器基础功能")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        print(f"[OK] 创建 Token 计数器")
        
        # 测试文本计数
        text = "Hello, world!"
        tokens = counter.count_text(text)
        assert tokens > 0
        print(f"[OK] 文本 Token 数: {tokens}")
        
        # 测试中文文本
        chinese_text = "你好，世界！"
        chinese_tokens = counter.count_text(chinese_text)
        assert chinese_tokens > 0
        print(f"[OK] 中文 Token 数: {chinese_tokens}")
        
        # 测试空文本
        empty_tokens = counter.count_text("")
        assert empty_tokens == 0
        print(f"[OK] 空文本 Token 数: {empty_tokens}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_counter_messages():
    """测试消息 Token 计数"""
    print("\n[TEST] 消息 Token 计数")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        
        # 测试简单消息
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        
        tokens = counter.count_messages(messages)
        assert tokens > 0
        print(f"[OK] 简单消息 Token 数: {tokens}")
        
        # 测试空消息列表
        empty_tokens = counter.count_messages([])
        assert empty_tokens == 0
        print(f"[OK] 空消息列表 Token 数: {empty_tokens}")
        
        # 测试复杂消息
        complex_messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant response"},
            {"role": "user", "content": "Follow-up question"},
        ]
        
        complex_tokens = counter.count_messages(complex_messages)
        assert complex_tokens > tokens
        print(f"[OK] 复杂消息 Token 数: {complex_tokens}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_limit_check():
    """测试 Token 限制检查"""
    print("\n[TEST] Token 限制检查")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        
        messages = [
            {"role": "user", "content": "Short message"}
        ]
        
        # 测试在限制内
        is_within, current = counter.check_limit(messages, max_tokens=1000)
        assert is_within
        print(f"[OK] 在限制内: {current} < 1000")
        
        # 测试超出限制
        is_within, current = counter.check_limit(messages, max_tokens=10)
        assert not is_within
        print(f"[OK] 超出限制: {current} > 10")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def test_message_truncation():
    """测试消息截断"""
    print("\n[TEST] 消息截断")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        
        # 创建长消息列表
        messages = [
            {"role": "system", "content": "System message"},
        ]
        
        for i in range(10):
            messages.append({"role": "user", "content": f"Message {i} with some additional text to make it longer"})
            messages.append({"role": "assistant", "content": f"Response {i} with detailed explanation and more content"})
        
        print(f"[INFO] 原始消息数: {len(messages)}")
        original_tokens = counter.count_messages(messages)
        print(f"[INFO] 原始 Token 数: {original_tokens}")
        
        # 截断消息（使用较小的限制）
        truncated = counter.truncate_messages(messages, max_tokens=100, keep_system=True)
        
        # 如果原始消息已经很短，可能不会截断
        if original_tokens > 100:
            assert len(truncated) < len(messages)
        assert truncated[0]["role"] == "system"  # 系统消息应该保留
        print(f"[OK] 截断后消息数: {len(truncated)}")
        
        # 测试不保留系统消息
        truncated_no_system = counter.truncate_messages(messages, max_tokens=100, keep_system=False)
        print(f"[OK] 不保留系统消息: {len(truncated_no_system)}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_token_estimation():
    """测试 Token 估算"""
    print("\n[TEST] Token 估算")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        
        # 测试英文估算
        english_text = "This is a test message with multiple words"
        estimated = counter.estimate_tokens(english_text)
        assert estimated > 0
        print(f"[OK] 英文估算: {estimated} tokens")
        
        # 测试中文估算
        chinese_text = "这是一个测试消息包含多个汉字"
        estimated = counter.estimate_tokens(chinese_text)
        assert estimated > 0
        print(f"[OK] 中文估算: {estimated} tokens")
        
        # 测试混合文本
        mixed_text = "Hello 你好 World 世界"
        estimated = counter.estimate_tokens(mixed_text)
        assert estimated > 0
        print(f"[OK] 混合文本估算: {estimated} tokens")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def test_token_counter_stats():
    """测试统计信息"""
    print("\n[TEST] 统计信息")
    
    try:
        counter = TokenCounter("gpt-3.5-turbo")
        
        stats = counter.get_stats()
        assert "model" in stats
        assert "tokenizer_available" in stats
        print(f"[OK] 统计信息: {stats}")
        
        return True
    
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def run_tests():
    """运行测试"""
    print("=" * 60)
    print("LLM Token 计数器测试")
    print("=" * 60)
    
    tests = [
        ("Token 计数器基础", test_token_counter_basic),
        ("消息 Token 计数", test_token_counter_messages),
        ("Token 限制检查", test_token_limit_check),
        ("消息截断", test_message_truncation),
        ("Token 估算", test_token_estimation),
        ("统计信息", test_token_counter_stats),
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
