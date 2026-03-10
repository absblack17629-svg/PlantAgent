# -*- coding: utf-8 -*-
"""
测试完整的工作流
"""

import asyncio
import sys
import os

sys.path.append(os.getcwd())

async def test_nine_node_workflow():
    """测试九节点工作流"""
    print('测试九节点工作流')
    print('='*60)
    
    try:
        from yoloapp.flow.nine_node_with_tools import run_nine_node_workflow
        
        # 测试用例1: 有图片的检测请求
        test_cases = [
            {
                'name': '检测请求（有图片）',
                'user_question': '检测这张图片中的水稻病害',
                'image_path': 'static/uploads/20260310_150832_71f62774.jpg'
            },
            {
                'name': '简单检测请求',
                'user_question': '检测图片',
                'image_path': 'static/uploads/20260310_150832_71f62774.jpg'
            },
            {
                'name': '中文检测请求',
                'user_question': '这是什么病',
                'image_path': 'static/uploads/20260310_150832_71f62774.jpg'
            }
        ]
        
        for test_case in test_cases:
            print(f'\n测试: {test_case["name"]}')
            print(f'问题: {test_case["user_question"]}')
            print(f'图片: {test_case["image_path"]}')
            
            result = await run_nine_node_workflow(
                test_case['user_question'],
                test_case['image_path']
            )
            
            print(f'成功: {result.get("success")}')
            print(f'意图: {result.get("intent")}')
            print(f'工具使用: {result.get("tools_used")}')
            print(f'响应长度: {len(result.get("response", ""))}')
            
            if result.get('tools_used'):
                print('[OK] 检测工具被调用')
            else:
                print('[ERROR] 检测工具未被调用')
                
            # 检查响应是否包含检测结果
            response = result.get('response', '')
            if '白叶枯病' in response or 'Bacterialblight' in response or '检测到' in response:
                print('[OK] 响应包含检测结果')
            else:
                print('[ERROR] 响应不包含检测结果')
        
        return True
        
    except Exception as e:
        print(f'工作流测试失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def test_intent_agent():
    """测试意图识别Agent"""
    print('\n测试意图识别Agent')
    print('='*60)
    
    try:
        from yoloapp.agent import IntentAgent
        from yoloapp.schema import Memory, Message
        
        test_cases = [
            ('检测这张图片', 'static/uploads/test.jpg'),
            ('这是什么病', 'static/uploads/test.jpg'),
            ('分析图片', 'static/uploads/test.jpg'),
            ('识别病害', 'static/uploads/test.jpg'),
        ]
        
        for user_input, image_path in test_cases:
            print(f'\n输入: {user_input}')
            print(f'图片: {image_path}')
            
            agent = IntentAgent()
            memory = Memory()
            memory.add_message(Message.user_message(user_input))
            memory.metadata['image_path'] = image_path
            agent.memory = memory
            
            await agent.step()
            
            intent = memory.metadata.get('intent', 'unknown')
            emotion = memory.metadata.get('emotion', 'unknown')
            
            print(f'识别意图: {intent}')
            print(f'识别情感: {emotion}')
            
            if intent == 'detect':
                print('[OK] 正确识别为检测意图')
            else:
                print('[ERROR] 未识别为检测意图')
        
        return True
        
    except Exception as e:
        print(f'意图Agent测试失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print('开始完整工作流测试...')
    
    tests = [
        ('九节点工作流', test_nine_node_workflow),
        ('意图识别Agent', test_intent_agent),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f'\n运行测试: {test_name}')
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f'测试执行异常: {e}')
            results.append((test_name, False))
    
    # 打印结果汇总
    print('\n' + '='*60)
    print('测试结果汇总')
    print('='*60)
    
    for test_name, success in results:
        status = '通过' if success else '失败'
        print(f'{test_name:20} {status}')
    
    print('\n分析:')
    print('如果九节点工作流测试失败但LangChain工具单独测试成功，')
    print('问题可能出现在:')
    print('1. 意图识别不准确')
    print('2. 工作流节点连接问题')
    print('3. 工具调用逻辑问题')

if __name__ == '__main__':
    asyncio.run(main())
