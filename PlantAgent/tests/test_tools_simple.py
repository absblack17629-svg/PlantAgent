# -*- coding: utf-8 -*-
"""
工具系统简单测试
"""

import asyncio
import os
import sys

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


async def test_base_tool():
    """测试 BaseTool"""
    print("\n[TEST] BaseTool 接口")
    
    try:
        tool = SimpleTool()
        print(f"[OK] 创建工具: {tool.name}")
        
        # 测试 to_param
        param = tool.to_param()
        assert param["type"] == "function"
        print(f"[OK] to_param 格式正确")
        
        # 测试执行
        result = await tool(value="test")
        assert result.success
        print(f"[OK] 工具执行成功")
        
        # 测试参数验证
        result = await tool()
        if not result.success:
            print(f"[OK] 参数验证正确")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def test_detection_tool():
    """测试检测工具"""
    print("\n[TEST] 检测工具")
    
    try:
        tool = DetectionTool()
        print(f"[OK] 创建检测工具")
        
        # 测试文件不存在
        result = await tool.execute(image_path="nonexistent.jpg")
        assert not result.success
        print(f"[OK] 文件不存在检测正确")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def test_knowledge_tool():
    """测试知识工具"""
    print("\n[TEST] 知识工具")
    
    try:
        tool = KnowledgeTool()
        print(f"[OK] 创建知识工具")
        
        # 测试查询
        result = await tool.execute(question="水稻病害有哪些？")
        assert result.success
        print(f"[OK] 知识查询成功")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def test_memory_tool():
    """测试记忆工具"""
    print("\n[TEST] 记忆工具")
    
    try:
        tool = MemoryTool()
        print(f"[OK] 创建记忆工具")
        
        # 测试创建任务
        result = await tool.execute(
            action="create_task",
            task_description="测试任务",
            steps="步骤1\n步骤2"
        )
        assert result.success
        print(f"[OK] 创建任务成功")
        
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


async def run_tests():
    """运行测试"""
    print("=" * 60)
    print("工具系统测试")
    print("=" * 60)
    
    tests = [
        ("BaseTool", test_base_tool),
        ("DetectionTool", test_detection_tool),
        ("KnowledgeTool", test_knowledge_tool),
        ("MemoryTool", test_memory_tool),
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
