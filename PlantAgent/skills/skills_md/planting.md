# Skill: 种植计划 (Planting Plan)

## 描述
根据土地面积、土壤类型、季节和地区，为用户制定详细的作物种植计划。

## 参数
- `land_area` (必填): 土地面积，单位为亩
- `soil_type` (必填): 土壤类型，可选值: 粘土、壤土、砂土、壤质粘土、砂质壤土
- `season` (必填): 种植季节，可选值: 春季、夏季、秋季、冬季
- `location` (必填): 所在地区/城市，用于参考气候条件

## 返回值格式
返回 JSON 格式的种植计划，包含:
- `success`: 是否成功生成计划 (boolean)
- `plan`: 种植计划详情，包含:
  - `crop`: 推荐种植的作物 (string)
  - `variety`: 推荐品种 (string)
  - `planting_density`: 种植密度 (string)
  - `expected_yield`: 预期产量 (string)
  - `growth_period`: 生长期 (string)
  - `rotation_suggestions`: 轮作建议 (array)
- `advice`: 额外的种植建议 (array)

## 使用示例
```
用户有 10 亩壤土，想在春季种植水稻。
1. 调用 skill 时传入 land_area=10, soil_type="壤土", season="春季", location="江苏南京"
2. 返回: {"success": true, "plan": {"crop": "水稻", "variety": "南粳系列", "planting_density": "每亩 1.5-2 万穴", "expected_yield": "每亩 600-700 公斤", ...}, "advice": ["注意防治纹枯病", "合理施肥"]}
```

## 注意事项
- 作物数据库包含水稻、小麦、玉米、大豆等主要作物
- 会根据地区气候自动调整种植时间
- 轮作建议帮助保持土壤肥力
- 考虑市场因素推荐经济效益好的品种