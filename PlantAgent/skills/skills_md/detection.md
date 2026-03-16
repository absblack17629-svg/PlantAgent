# Skill: 水稻病害检测 (Rice Disease Detection)

## 描述
使用 YOLO11 模型检测图片中的水稻病害，返回病害类型、位置和置信度。

## 参数
- `image_path` (必填): 图片文件的绝对路径或相对于项目根目录的路径
- `confidence_threshold` (可选): 置信度阈值，低于此值的检测结果将被过滤，默认为 0.5

## 返回值格式
返回 JSON 格式的检测结果，包含:
- `success`: 是否检测成功 (boolean)
- `detections`: 检测结果数组，每个元素包含:
  - `class_name`: 病害类别名称 (string)
  - `confidence`: 置信度 0-1 (number)
  - `bbox`: 边界框坐标 [x1, y1, x2, y2] (array)
- `image_path`: 被检测的图片路径 (string)
- `detection_count`: 检测到的病害总数 (number)

## 使用示例
```
用户上传了一张水稻叶片照片，要求检测病害。
1. 调用 skill 时传入 image_path="uploads/photo.jpg"
2. 返回结果可能如: {"success": true, "detections": [{"class_name": "稻瘟病", "confidence": 0.89, "bbox": [100, 50, 300, 200]}], "detection_count": 1}
```

## 注意事项
- 支持的图片格式: jpg, jpeg, png, bmp
- 图片文件必须存在且可读
- 如果未检测到任何病害，返回空的 detections 数组
- 常见的病害类别包括: 稻瘟病、白叶枯病、纹枯病、稻曲病等