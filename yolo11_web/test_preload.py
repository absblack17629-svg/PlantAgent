# -*- coding: utf-8 -*-
"""
测试预加载功能
验证所有模型和服务是否正确预加载
"""

import asyncio
import time


async def test_preload():
    """测试预加载功能"""
    print("=" * 60)
    print("[TEST] 测试预加载功能")
    print("=" * 60)
    
    results = []
    
    # 1. 测试 YOLO 模型
    print("\n[1/4] 测试 YOLO 检测模型...")
    start = time.time()
    try:
        from services.detection_service import get_detection_service
        detection_service = get_detection_service()
        
        if detection_service.yolo_model is not None:
            elapsed = time.time() - start
            print(f"[OK] YOLO 模型已加载 (耗时: {elapsed:.2f}秒)")
            results.append(("YOLO模型", True, elapsed))
        else:
            print("[ERROR] YOLO 模型未加载")
            results.append(("YOLO模型", False, 0))
    except Exception as e:
        print(f"[ERROR] YOLO 模型测试失败: {e}")
        results.append(("YOLO模型", False, 0))
    
    # 2. 测试 RAG 服务
    print("\n[2/4] 测试 RAG 服务...")
    start = time.time()
    try:
        from yoloapp.rag import get_rag_service
        rag_service = get_rag_service()
        
        # 如果还没初始化，现在初始化
        if not rag_service._initialized:
            await rag_service.init_async()
        
        if rag_service._initialized:
            elapsed = time.time() - start
            print(f"[OK] RAG 服务已加载 (耗时: {elapsed:.2f}秒)")
            results.append(("RAG服务", True, elapsed))
        else:
            print("[ERROR] RAG 服务未加载")
            results.append(("RAG服务", False, 0))
    except Exception as e:
        print(f"[ERROR] RAG 服务测试失败: {e}")
        results.append(("RAG服务", False, 0))
    
    # 3. 测试 LLM 客户端
    print("\n[3/4] 测试 LLM 客户端...")
    start = time.time()
    try:
        from yoloapp.llm import get_llm_client
        llm = get_llm_client("default")
        
        if llm is not None:
            elapsed = time.time() - start
            print(f"[OK] LLM 客户端已加载 (耗时: {elapsed:.2f}秒)")
            results.append(("LLM客户端", True, elapsed))
        else:
            print("[ERROR] LLM 客户端未加载")
            results.append(("LLM客户端", False, 0))
    except Exception as e:
        print(f"[ERROR] LLM 客户端测试失败: {e}")
        results.append(("LLM客户端", False, 0))
    
    # 4. 测试 LangGraph 工作流
    print("\n[4/4] 测试 LangGraph 工作流...")
    start = time.time()
    try:
        from yoloapp.flow.nine_node_with_tools import get_or_create_workflow
        workflow = get_or_create_workflow()
        
        if workflow is not None:
            elapsed = time.time() - start
            print(f"[OK] LangGraph 工作流已编译 (耗时: {elapsed:.2f}秒)")
            results.append(("LangGraph工作流", True, elapsed))
        else:
            print("[ERROR] LangGraph 工作流未加载")
            results.append(("LangGraph工作流", False, 0))
    except Exception as e:
        print(f"[ERROR] LangGraph 工作流测试失败: {e}")
        results.append(("LangGraph工作流", False, 0))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("[CHART] 预加载测试结果汇总")
    print("=" * 60)
    
    total = len(results)
    success = sum(1 for _, status, _ in results if status)
    total_time = sum(elapsed for _, _, elapsed in results)
    
    for name, status, elapsed in results:
        status_icon = "[OK]" if status else "[ERROR]"
        time_str = f"{elapsed:.2f}秒" if elapsed > 0 else "失败"
        print(f"{status_icon} {name:20s} {time_str}")
    
    print("-" * 60)
    print(f"成功率: {success}/{total} ({success/total*100:.1f}%)")
    print(f"总耗时: {total_time:.2f}秒")
    print("=" * 60)
    
    if success == total:
        print("[CELEBRATE] 所有组件预加载成功！")
    else:
        print("[WARNING] 部分组件预加载失败，请检查日志")


if __name__ == "__main__":
    asyncio.run(test_preload())
