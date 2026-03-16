# -*- coding: utf-8 -*-
"""
工具系统测试

测试 BaseTool 和具体工具实现。
"""

import asyncio
import os
import sys
from typing import Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tools.base import BaseTool, ToolResult
from services.tools.detection_tool import DetectionTool, CacheTool
from services.tools.knowledge_tool import KnowledgeTool, DetectionAnalysisTool
from services.tools.memory_tool import MemoryTool
from services.exceptions import ToolError


# 测试用的简单工具
class SimpleTool(BaseTool):
    """简单测试工具"""
    
    name: str = "simple_tool"
    description: str = "简单的测试工具"
    parameters: dict = {
        "type": "object",
        "properties": {
            "value": {"type": "string"}
        },
        "required": ["value"]
    }
    
    async def execute(self, value: str, **kwargs) -> ToolResult:
        """执行工具"""
        return self.success_response(
            data={"result": f"处理了: {value}"},
            message="执行成功"
        )


async def test_base_tool_interface():
    """测试 BaseTool 接口"""
    print("\n=== 测试 BaseTool 接口 ===")
    
    try:
        # 创建工具
        tool = SimpleTool()
        print(f"✅ 创建工具: {tool.name}")
        
        # 测试 to_param
        param = tool.to_param()
        assert param["type"] == "function"
        assert param["function"]["name"] == "simple_tool"
        print(f"✅ to_param 格式正确")
        
        # 测试执行
        result = await tool(value="test")
        assert result.success
        assert result.output["result"] == "处理了: test"
        print(f"✅ 工具执行成功: {result.output}")
        
        # 测试参数验证
        try:
            result = await tool()  # 缺少必需参数
            # 如果返回了失败结果而不是抛出异常，也是可以的
            if not result.success:
                print(f"✅ 参数验证正确（返回失败结果）: {result.error}")
            else:
                print(f"❌ 应该返回失败结果或抛出参数错误")
                return False
        except ToolError as e:
            print(f"✅ 参数验证正确（抛出异常）: {e.message}")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tool_result():
    """测试 ToolResult 行为"""
    print("\n=== 测试 ToolResult ===")
    
    try:
        # 测试成功结果
        success_result = ToolResult(
            output="成功数据",
            success=True,
            metadata={"tool": "test"}
        )
        
        assert success_result.success
        assert bool(success_result)  # __bool__
        assert "成功数据" in str(success_result)  # __str__
        print(f"✅ 成功结果: {success_result}")
        
        # 测试失败结果
        fail_result = ToolResult(
            error="错误信息",
            success=False,
            metadata={"tool": "test"}
        )
        
        assert not fail_result.success
        assert not bool(fail_result)  # __bool__
        assert "Error" in str(fail_result)  # __str__
        print(f"✅ 失败结果: {fail_result}")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_detection_tool():
    """测试检测工具"""
    print("\n=== 测试检测工具 ===")
    
    try:
        # 创建工具
        tool = DetectionTool()
        print(f"✅ 创建检测工具: {tool.name}")
        
        # 测试文件不存在
        result = await tool.execute(image_path="nonexistent.jpg")
        assert not result.success
        assert "不存在" in result.error
        print(f"✅ 文件不存在检测正确")
        
        # 测试 to_param
        param = tool.to_param()
        assert "image_path" in param["function"]["parameters"]["properties"]
        print(f"✅ 参数定义正确")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_cache_tool():
    """测试缓存工具"""
    print("\n=== 测试缓存工具 ===")
    
    try:
        # 创建工具
        tool = CacheTool()
        print(f"✅ 创建缓存工具: {tool.name}")
        
        # 测试获取统计
        result = await tool.execute(action="stats")
        assert result.success
        assert "cache_dir" in result.output
        print(f"✅ 获取统计成功")
        
        # 测试清理缓存
        result = await tool.execute(action="clear")
        assert result.success
        print(f"✅ 清理缓存成功")
        
        # 测试无效操作
        result = await tool.execute(action="invalid")
        assert not result.success
        print(f"✅ 无效操作检测正确")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_tool():
    """测试知识工具"""
    print("\n=== 测试知识工具 ===")
    
    try:
        # 创建工具
        tool = KnowledgeTool()
        print(f"✅ 创建知识工具: {tool.name}")
        
        # 测试超出范围问题
        result = await tool.execute(question="今天天气怎么样？")
        assert result.success
        assert "超出范围" in result.output["answer"] or "不在我的专业范围" in result.output["answer"]
        print(f"✅ 超出范围检测正确")
        
        # 测试水稻相关问题
        result = await tool.execute(question="水稻病害有哪些？")
        assert result.success
        assert "水稻" in result.output["answer"]
        print(f"✅ 水稻问题回答正确")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_detection_analysis_tool():
    """测试检测分析工具"""
    print("\n=== 测试检测分析工具 ===")
    
    try:
        # 创建工具
        tool = DetectionAnalysisTool()
        print(f"✅ 创建分析工具: {tool.name}")
        
        # 测试分析（无病害）
        result = await tool.execute(
            question="这是什么病害？",
            detections="未检测到任何对象"
        )
        assert result.success
        assert result.output["count"] == 0
        print(f"✅ 无病害分析正确")
        
        # 测试分析（有病害）
        detections_text = """检测到 1 个对象：
1. 细菌性条斑病 (置信度: 0.88)
"""
        result = await tool.execute(
            question="这是什么病害？",
            detections=detections_text
        )
        assert result.success
        assert result.output["count"] > 0
        print(f"✅ 病害分析正确: 检测到 {result.output['count']} 个病害")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_tool():
    """测试记忆工具"""
    print("\n=== 测试记忆工具 ===")
    
    try:
        # 创建工具
        tool = MemoryTool()
        print(f"✅ 创建记忆工具: {tool.name}")
        
        # 测试创建任务
        result = await tool.execute(
            action="create_task",
            task_description="测试任务",
            steps="步骤1\n步骤2"
        )
        assert result.success
        task_id = result.output["task_id"]
        print(f"✅ 创建任务成功: {task_id}")
        
        # 测试更新任务
        result = await tool.execute(
            action="update_task",
            task_id=task_id,
            current_step="完成步骤1",
            status="in_progress"
        )
        assert result.success
        print(f"✅ 更新任务成功")
        
        # 测试获取当前任务
        result = await tool.execute(action="get_current_task")
        assert result.success
        assert result.output is not None
        print(f"✅ 获取当前任务成功")
        
        # 测试保存上下文
        result = await tool.execute(
            action="save_context",
            context="测试上下文",
            context_type="test"
        )
        assert result.success
        print(f"✅ 保存上下文成功")
        
        # 测试搜索
        result = await tool.execute(
            action="search",
            query="测试",
            limit=5
        )
        assert result.success
        print(f"✅ 搜索成功")
        
        # 测试获取统计
        result = await tool.execute(action="stats")
        assert result.success
        print(f"✅ 获取统计成功")
        
        return True
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("工具系统测试")
    print("=" * 60)
    
    tests = [
        ("BaseTool 接口", test_base_tool_interface),
        ("ToolResult 行为", test_tool_result),
        ("检测工具", test_detection_tool),
        ("缓存工具", test_cache_tool),
        ("知识工具", test_knowledge_tool),
        ("检测分析工具", test_detection_analysis_tool),
        ("记忆工具", test_memory_tool),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] 测试 {name} 异常: {e}")
            results.append((name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
