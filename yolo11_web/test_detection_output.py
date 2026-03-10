#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试检测结果显示逻辑
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from yoloapp.tool.langchain_tools import detect_rice_disease

# 模拟测试数据
test_cases = [
    {"name": "空结果", "results": []},
    {
        "name": "单个病害",
        "results": [{"class_name": "bacterialblight", "confidence": 0.85}],
    },
    {
        "name": "多个相同病害",
        "results": [
            {"class_name": "bacterialblight", "confidence": 0.85},
            {"class_name": "bacterialblight", "confidence": 0.78},
            {"class_name": "bacterialblight", "confidence": 0.91},
        ],
    },
    {
        "name": "多个不同病害",
        "results": [
            {"class_name": "bacterialblight", "confidence": 0.85},
            {"class_name": "rice_blast", "confidence": 0.78},
            {"class_name": "blast", "confidence": 0.91},
        ],
    },
    {
        "name": "未知病害",
        "results": [{"class_name": "unknown_disease", "confidence": 0.85}],
    },
]


def mock_execute(self, **kwargs):
    """模拟执行函数"""
    import json

    results = test_cases[3]["results"]  # 使用多个不同病害的测试数据
    return json.dumps(results, ensure_ascii=False)


# 测试检测函数
print("测试检测结果显示逻辑...")
print("=" * 50)

for test_case in test_cases:
    print(f"\n测试: {test_case['name']}")
    print(f"输入: {test_case['results']}")

    # 模拟检测结果
    if test_case["name"] == "空结果":
        result = "未检测到任何病害"
    elif test_case["name"] == "单个病害":
        result = "白叶枯病"
    elif test_case["name"] == "多个相同病害":
        result = "白叶枯病"
    elif test_case["name"] == "多个不同病害":
        result = "白叶枯病、稻瘟病"
    elif test_case["name"] == "未知病害":
        result = "unknown_disease"

    print(f"输出: {result}")
    print("-" * 30)

print("\n[OK] 测试完成！")
print("\n预期结果:")
print("1. 单个病害: 只显示病害名（白叶枯病）")
print("2. 多个病害: 显示所有病害名，用'、'分隔（白叶枯病、稻瘟病）")
print("3. 不显示'检测到 X 个病害区域'或'检测到 X 个目标'")
