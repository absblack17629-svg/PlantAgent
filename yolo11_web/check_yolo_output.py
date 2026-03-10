# -*- coding: utf-8 -*-
"""
检查YOLO模型输出
"""

import asyncio
import sys
import os

sys.path.append(".")


async def check_yolo_output():
    """检查YOLO模型原始输出"""
    try:
        from ultralytics import YOLO
        from config.settings import settings

        print("Loading YOLO model...")
        model = YOLO(settings.MODEL_PATH)
        print("Model loaded")

        # 测试推理
        test_image = "bus.jpg"
        if os.path.exists(test_image):
            print(f"Running inference on: {test_image}")
            results = model.predict(source=test_image, verbose=False)

            print(f"Number of results: {len(results)}")

            for i, r in enumerate(results):
                print(f"\nResult {i}:")
                print(f"  Type: {type(r)}")
                print(f"  Has boxes: {hasattr(r, 'boxes')}")

                if hasattr(r, "boxes") and r.boxes is not None:
                    print(f"  Number of boxes: {len(r.boxes)}")
                    for j, box in enumerate(r.boxes):
                        print(f"    Box {j}:")
                        print(f"      Class: {box.cls}")
                        print(f"      Confidence: {box.conf}")
                        print(f"      Coordinates: {box.xyxy}")

                        # 检查类名
                        if hasattr(model, "names"):
                            class_id = int(box.cls)
                            class_name = model.names[class_id]
                            print(f"      Class name: {class_name}")

                            # 检查类名是否包含非ASCII字符
                            try:
                                class_name.encode("gbk")
                                print(f"      GBK encoding: OK")
                            except UnicodeEncodeError as e:
                                print(f"      GBK encoding error: {e}")
                                print(
                                    f"      Character causing error: {repr(class_name)}"
                                )

                # 检查其他属性
                for attr in ["probs", "keypoints", "masks"]:
                    if hasattr(r, attr) and getattr(r, attr) is not None:
                        print(f"  Has {attr}: Yes")

        else:
            print(f"Test image not found: {test_image}")

    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_yolo_output())
