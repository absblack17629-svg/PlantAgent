# -*- coding: utf-8 -*-
"""
测试病害类型映射
验证所有可能的病害名称格式都能正确映射到防治方案
"""

from services.enhanced_detection_service import EnhancedDetectionService

def test_disease_mapping():
    """测试病害映射"""
    service = EnhancedDetectionService()
    
    # 测试用例：各种可能的病害名称格式
    test_cases = [
        # 褐斑病的各种格式
        ("Brownspot", "褐斑病"),
        ("Browspot", "褐斑病"),  # 拼写变体
        ("Brown spot", "褐斑病"),
        ("Brow spot", "褐斑病"),
        ("brown_spot", "褐斑病"),
        ("brow_spot", "褐斑病"),
        ("brownspot", "褐斑病"),
        ("browspot", "褐斑病"),
        ("褐斑病", "褐斑病"),
        
        # 白叶枯病
        ("Bacterialblight", "白叶枯病"),
        ("bacterial_blight", "白叶枯病"),
        ("白叶枯病", "白叶枯病"),
        
        # 稻瘟病
        ("Blast", "稻瘟病"),
        ("rice_blast", "稻瘟病"),
        ("稻瘟病", "稻瘟病"),
    ]
    
    print("=" * 60)
    print("病害类型映射测试")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for input_name, expected_chinese in test_cases:
        scheme = service._get_prevention_scheme(input_name)
        
        # 检查是否包含预期的病害名称
        if expected_chinese in scheme and "未找到该病害的防治方案" not in scheme:
            print(f"[OK] {input_name:20s} -> {expected_chinese}")
            passed += 1
        else:
            print(f"[ERROR] {input_name:20s} -> 未找到防治方案")
            failed += 1
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    # 显示一个完整的防治方案示例
    if passed > 0:
        print("\n褐斑病防治方案示例:")
        print("-" * 60)
        scheme = service._get_prevention_scheme("Browspot")
        print(scheme[:300] + "...")

if __name__ == "__main__":
    test_disease_mapping()
