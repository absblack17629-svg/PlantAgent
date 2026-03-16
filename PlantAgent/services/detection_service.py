# -*- coding: utf-8 -*-
"""
目标检测服务
负责YOLO模型的加载和目标检测功能（异步版本）
"""

import os
import traceback
import asyncio
from typing import List, Dict, Optional
from config.settings import settings


class DetectionService:
    """目标检测服务类（异步版本）"""

    def __init__(self):
        self.yolo_model = None
        self._load_yolo_model()

    def _load_yolo_model(self):
        """加载YOLO11模型"""
        try:
            print("初始化YOLO11目标检测模型...")

            # 动态导入（避免在不支持的环境报错）
            from ultralytics import YOLO

            # 从配置文件加载模型
            self.yolo_model = YOLO(settings.MODEL_PATH)
            print(f"YOLO11模型加载成功（路径：{settings.MODEL_PATH}）")

            # 测试模型推理能力
            self._test_model_inference()

        except Exception as e:
            print(f"[ERROR] YOLO11模型加载失败：{str(e)}")
            print(f"[DETAIL] 详细信息：{traceback.format_exc()}")
            self.yolo_model = None

    def _test_model_inference(self):
        """测试模型推理能力"""
        try:
            # 创建一个简单的测试图片（白色背景）
            import numpy as np
            from PIL import Image

            test_img = np.ones((640, 640, 3), dtype=np.uint8) * 255
            test_img = Image.fromarray(test_img)

            # Windows兼容路径
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                test_path = tmp.name
                test_img.save(test_path)

            # 使用测试图片进行推理
            self.yolo_model.predict(source=test_path, verbose=False)
            print("YOLO模型推理能力正常，可以开始检测任务了！")

            # 清理测试文件
            try:
                os.remove(test_path)
            except:
                pass
        except Exception as test_e:
            print(f"[WARNING] 模型推理测试失败，但模型加载成功：{str(test_e)}")
            print("[INFO] 这不影响正常功能，上传图片时会重新测试")

    async def detect_objects(self, image_path: str) -> List[Dict]:
        """
        执行目标检测（异步版本）

        Args:
            image_path: 图片文件路径

        Returns:
            检测结果列表
        """
        print(f"[DETECT] 开始检测图片：{image_path}")
        print(f"[INFO] 图片是否存在：{os.path.exists(image_path)}")

        # 检查模型是否可用
        if not self.yolo_model:
            print("[WARNING] YOLO模型未加载，无法进行检测")
            return []

        try:
            # 在线程池中执行YOLO检测（因为YOLO是同步的）
            loop = asyncio.get_event_loop()
            detections = await loop.run_in_executor(None, self._sync_detect, image_path)

            return detections

        except Exception as e:
            print(f"[ERROR] YOLO检测过程中出现错误：{str(e)}")
            print(f"[ERROR] 错误详情：{traceback.format_exc()}")
            return []

    def _sync_detect(self, image_path: str) -> List[Dict]:
        """同步检测方法（在线程池中执行）"""
        print("[RUN] 正在运行YOLO推理...")
        results = self.yolo_model(image_path, verbose=False)

        # 解析检测结果
        detections = []
        total_boxes = 0

        for r in results:
            if hasattr(r, "boxes") and r.boxes is not None:
                boxes_count = len(r.boxes)
                total_boxes += boxes_count
                print(f"   [FOUND] 在这张图片中发现 {boxes_count} 个目标")

                for i, box in enumerate(r.boxes):
                    # 提取检测信息
                    class_id = int(box.cls)
                    class_name = self.yolo_model.names[class_id]
                    confidence = round(float(box.conf), 2)
                    bbox = [round(x, 2) for x in box.xyxy.tolist()[0]]

                    # 调试：打印每个检测框
                    print(f"      [TARGET] 目标{i + 1}: {class_name} (置信度:{confidence})")
                    print(f"         [BBOX] 位置: {bbox}")

                    # 添加到结果列表
                    detections.append(
                        {
                            "类别": class_name,
                            "置信度": confidence,
                            "坐标": bbox,  # [x1, y1, x2, y2] 左上角和右下角坐标
                        }
                    )

        print(f"[SUCCESS] 检测完成！共发现 {len(detections)} 个目标")
        return detections
