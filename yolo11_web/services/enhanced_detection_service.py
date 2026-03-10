# -*- coding: utf-8 -*-
"""
增强版检测服务
水稻病害检测 - 包含病害类型映射和防治方案
"""

import os
import uuid
import time
from typing import Dict, List, Optional
from datetime import datetime

import config
from services.detection_service import DetectionService as BaseDetectionService


# 病害类型映射 - YOLO类别到中文病害名称
DISEASE_MAPPING = {
    "bacterial_blight": {
        "disease_type": "白叶枯病",
        "disease_name": "水稻白叶枯病",
        "severity_levels": {
            (0, 0.3): "mild",
            (0.3, 0.7): "moderate",
            (0.7, 1.0): "severe",
        },
        "description": "细菌性病害，表现为叶片叶尖或叶缘产生黄绿色或暗绿色斑点",
    },
    "rice_blast": {
        "disease_type": "稻瘟病",
        "disease_name": "水稻稻瘟病",
        "severity_levels": {
            (0, 0.3): "mild",
            (0.3, 0.7): "moderate",
            (0.7, 1.0): "severe",
        },
        "description": "真菌性病害，可分为叶瘟、节瘟、穗颈瘟，造成白穗",
    },
    "brown_spot": {
        "disease_type": "褐斑病",
        "disease_name": "水稻褐斑病",
        "severity_levels": {
            (0, 0.3): "mild",
            (0.3, 0.7): "moderate",
            (0.7, 1.0): "severe",
        },
        "description": "真菌性病害，叶片上产生褐色椭圆形病斑",
    },
    "healthy": {
        "disease_type": "健康",
        "disease_name": "健康水稻",
        "severity_levels": {},
        "description": "水稻生长正常，未发现病害症状",
    },
}

# 简化映射 - 如果模型只输出数字
SIMPLE_DISEASE_MAPPING = {0: "白叶枯病", 1: "稻瘟病", 2: "褐斑病", 3: "健康"}


class EnhancedDetectionService:
    """
    增强版检测服务
    在基础检测服务上添加病害分析、防治方案等功能
    """

    def __init__(self):
        self.base_service = BaseDetectionService()
        self.confidence_threshold = config.settings.MODEL_CONFIDENCE_THRESHOLD

    async def detect(self, image_path: str, user_id: str = None) -> Dict:
        """
        执行病害检测

        Args:
            image_path: 图片路径
            user_id: 用户ID

        Returns:
            检测结果字典
        """
        start_time = time.time()

        # 基础检测
        raw_detections = await self.base_service.detect_objects(image_path)

        # 处理检测结果
        detections = []
        disease_found = False

        for det in raw_detections:
            confidence = det.get("置信度", 0)

            # 过滤低置信度检测
            if confidence < self.confidence_threshold:
                continue

            class_name = det.get("类别", "")

            # 映射病害类型
            disease_info = self._map_disease(class_name, confidence)

            detection = {
                "class": class_name,
                "disease_type": disease_info["disease_type"],
                "disease_name": disease_info["disease_name"],
                "confidence": confidence,
                "bbox": det.get("坐标", []),
                "severity": disease_info["severity"],
                "description": disease_info["description"],
            }

            detections.append(detection)

            if disease_info["disease_type"] != "健康":
                disease_found = True

        # 检测耗时
        duration = int((time.time() - start_time) * 1000)

        # 构建结果
        result = {
            "success": True,
            "detections": detections,
            "disease_found": disease_found,
            "detection_time": datetime.now().isoformat(),
            "duration_ms": duration,
            "image_path": image_path,
            "model_version": "yolo11n-enhanced-v1.0",
        }

        # 添加主要病害信息
        if detections:
            main_detection = detections[0]
            result["disease_type"] = main_detection["disease_type"]
            result["confidence"] = main_detection["confidence"]
            result["severity"] = main_detection["severity"]

            # 添加防治方案
            if main_detection["disease_type"] != "健康":
                result["prevention_scheme"] = self._get_prevention_scheme(
                    main_detection["disease_type"]
                )
        else:
            result["disease_type"] = "未检测到病害"
            result["confidence"] = 0
            result["severity"] = "none"

        return result

    def _map_disease(self, class_name: str, confidence: float) -> Dict:
        """
        映射检测类别到病害信息

        Args:
            class_name: YOLO检测类别
            confidence: 置信度

        Returns:
            病害信息字典
        """
        # 统一处理字符串
        if isinstance(class_name, int):
            class_name = str(class_name)

        original_name = str(class_name)

        # 规范化类别名称（统一转换为小写，去除空格和下划线）
        normalized_name = str(class_name).lower().strip()
        normalized_name = normalized_name.replace(" ", "_").replace("-", "_")

        # 尝试从预定义映射获取（使用规范化名称）
        mapping = None
        for key in DISEASE_MAPPING:
            normalized_key = key.lower().strip().replace(" ", "_").replace("-", "_")
            if normalized_name == normalized_key:
                mapping = DISEASE_MAPPING[key]
                break

        # 如果没有找到，尝试模糊匹配（处理拼写变体）
        if mapping is None:
            # 检查是否是常见的拼写错误（缺少n的情况）
            if "brow" in normalized_name:
                # 尝试使用brown替代brow
                corrected_name = normalized_name.replace("brow", "brown")
                for key in DISEASE_MAPPING:
                    normalized_key = (
                        key.lower().strip().replace(" ", "_").replace("-", "_")
                    )
                    if corrected_name == normalized_key:
                        mapping = DISEASE_MAPPING[key]
                        break

        # 如果没有找到，尝试模糊匹配（处理拼写变体）
        if mapping is None:
            # 常见拼写变体映射
            variant_mapping = {
                "brow_spot": "brown_spot",  # 缺少n的拼写
                "browspot": "brownspot",  # 缺少n的拼写
                "brow_spot": "brown_spot",  # 缺少n的拼写
                "brow spot": "brown spot",  # 缺少n的拼写
            }

            # 检查是否是常见拼写变体
            for variant, correct in variant_mapping.items():
                if normalized_name == variant.lower().replace(" ", "_").replace(
                    "-", "_"
                ):
                    # 使用正确的名称查找映射
                    for key in DISEASE_MAPPING:
                        normalized_key = (
                            key.lower().strip().replace(" ", "_").replace("-", "_")
                        )
                        if (
                            correct.replace(" ", "_").replace("-", "_")
                            == normalized_key
                        ):
                            mapping = DISEASE_MAPPING[key]
                            break
                    break

        if mapping is None:
            # 尝试简化映射（数字）
            if normalized_name.isdigit():
                disease_type = SIMPLE_DISEASE_MAPPING.get(
                    int(normalized_name), "未知病害"
                )
            else:
                # 尝试中文匹配
                disease_type = "未知病害"
                for key, value in DISEASE_MAPPING.items():
                    if value["disease_type"] == class_name:
                        disease_type = class_name
                        mapping = value
                        break

                if disease_type == "未知病害":
                    disease_type = class_name

                    # 创建默认映射
                    mapping = {
                        "disease_type": disease_type,
                        "disease_name": disease_type,
                        "severity_levels": {},
                        "description": "检测到病害",
                    }

        # 确定严重程度
        severity = "mild"
        for (low, high), level in mapping.get("severity_levels", {}).items():
            if low <= confidence < high:
                severity = level
                break

        return {
            "disease_type": mapping["disease_type"],
            "disease_name": mapping.get("disease_name", mapping["disease_type"]),
            "severity": severity,
            "description": mapping.get("description", ""),
        }

    def _get_prevention_scheme(self, disease_type: str) -> str:
        """
        获取病害防治方案

        Args:
            disease_type: 病害类型

        Returns:
            防治方案文本
        """
        # 规范化病害类型（用于映射）
        normalized_type = disease_type.lower().strip()

        # 病害类型别名映射（支持多种输入格式）
        disease_aliases = {
            "白叶枯病": [
                "白叶枯病",
                "白叶枯",
                "bacterial blight",
                "bacterialblight",
                "bacterial_blight",
            ],
            "稻瘟病": ["稻瘟病", "稻瘟", "blast", "rice blast", "rice_blast"],
            "褐斑病": [
                "褐斑病",
                "褐斑",
                "brown spot",
                "brownspot",
                "brown_spot",
                "brow spot",
                "browspot",
            ],
            "健康": ["健康", "healthy", "正常", "无病害"],
        }

        # 查找标准病害类型
        standard_type = "未知病害"
        for std_type, aliases in disease_aliases.items():
            if disease_type in aliases or normalized_type in [
                a.lower() for a in aliases
            ]:
                standard_type = std_type
                break

        # 防治方案
        schemes = {
            "白叶枯病": """
## 白叶枯病防治方案

### 病害类型
细菌性病害

### 症状识别
叶片叶尖或叶缘产生黄绿色或暗绿色斑点，后沿叶脉扩展成条斑，病斑灰白色，病健部交界线明显，呈波纹状。湿度大时病斑上产生黄色菌脓。

### 防治方法
1. **农业防治**：选用抗病品种，健身栽培，科学管水，合理施肥
2. **化学防治**：发病初期用20%噻菌铜悬浮剂600倍液，或50%氯溴异氰尿酸可溶粉剂1000倍液喷雾
3. **发病时期**：水稻分蘖至孕穗期注意防治

### 预防措施
- 选用抗病品种
- 避免偏施氮肥
- 及时清除病残体
- 科学管水，防止串灌
""",
            "稻瘟病": """
## 稻瘟病防治方案

### 病害类型
真菌性病害

### 症状识别
叶瘟：梭形病斑，外黄褐色，中灰白色，有褐色坏死线
节瘟：节上产生褐色小点，后绕节扩展，使节部变黑褐色，易折断
穗颈瘟：穗颈上产生褐色小点，后扩展成黑褐色条斑，造成白穗

### 防治方法
1. **农业防治**：选用抗病品种，健身栽培，消灭菌源
2. **化学防治**：发病初期用75%三环唑可湿性粉剂2000倍液，或40%稻瘟灵乳油800倍液喷雾
3. **发病时期**：分蘖期、抽穗期易发病，需重点关注

### 预防措施
- 选用抗病品种
- 合理施肥，避免氮肥过多
- 及时处理病稻草
- 保持田间通风透光
""",
            "褐斑病": """
## 褐斑病防治方案

### 病害类型
真菌性病害

### 症状识别
叶片上产生褐色椭圆形病斑，大小约3-14×2-6mm，病斑中央灰褐色，边缘褐色，外围有黄色晕圈。病斑多时连成不规则大斑。

### 防治方法
1. **农业防治**：清除病残体，科学施肥，增施钾肥
2. **化学防治**：发病初期用50%多菌灵可湿性粉剂800倍液，或70%甲基硫菌灵可湿性粉剂1000倍液喷雾
3. **发病时期**：水稻生长中后期注意防治

### 预防措施
- 清除田间病残体
- 合理施肥，增强植株抗病力
- 避免偏施氮肥
- 发病初期及时喷药
""",
            "健康": """
## 水稻生长正常

恭喜！您的水稻目前生长健康，未发现病害症状。

### 建议
1. 继续保持良好的田间管理
2. 合理施肥，科学管水
3. 定期观察水稻生长情况
4. 提前预防病害发生
""",
        }

        return schemes.get(standard_type, "未找到该病害的防治方案")

    def get_detection_stats(self, detections: List[Dict]) -> Dict:
        """
        获取检测统计信息

        Args:
            detections: 检测结果列表

        Returns:
            统计信息字典
        """
        if not detections:
            return {"total": 0, "by_type": {}, "by_severity": {}, "avg_confidence": 0}

        by_type = {}
        by_severity = {}
        total_confidence = 0

        for det in detections:
            dtype = det.get("disease_type", "未知")
            severity = det.get("severity", "unknown")
            conf = det.get("confidence", 0)

            by_type[dtype] = by_type.get(dtype, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
            total_confidence += conf

        return {
            "total": len(detections),
            "by_type": by_type,
            "by_severity": by_severity,
            "avg_confidence": round(total_confidence / len(detections), 2),
        }


# 全局实例
_detection_service = None


def get_enhanced_detection_service() -> EnhancedDetectionService:
    """获取增强版检测服务单例"""
    global _detection_service
    if _detection_service is None:
        _detection_service = EnhancedDetectionService()
    return _detection_service
