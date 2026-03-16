# Skill: 智能灌溉 (Smart Irrigation)

## 描述
根据作物类型、生长阶段、土壤湿度和天气预报，智能推荐灌溉方案。

## 参数
- `crop_type` (必填): 作物类型，可选值: 水稻、小麦、玉米、大豆
- `growth_stage` (必填): 生长阶段，不同作物有不同的阶段:
  - 水稻: 秧苗期、分蘖期、拔节期、抽穗期、灌浆期、成熟期
  - 小麦: 播种期、分蘖期、拔节期、抽穗期、灌浆期、成熟期
  - 玉米: 播种期、苗期、拔节期、大喇叭口期、抽雄期、灌浆期、成熟期
  - 大豆: 播种期、苗期、分枝期、开花期、结荚期、鼓粒期、成熟期
- `soil_moisture` (可选): 土壤湿度百分比 0-100，默认为 60
- `rain_expected` (可选): 未来 24 小时是否有雨，默认为 false

## 返回值格式
返回 JSON 格式的灌溉建议，包含:
- `success`: 是否成功生成建议 (boolean)
- `recommendation`: 灌溉建议:
  - `should_irrigate`: 是否需要灌溉 (boolean)
  - `water_amount`: 推荐灌溉量 (string, 如 "每亩 30-40 立方米")
  - `irrigation_method`: 推荐灌溉方式 (string)
  - `best_time`: 最佳灌溉时间 (string)
  - `reason`: 建议原因 (string)
- `notes`: 注意事项数组 (array)

## 使用示例
```
用户种植的水稻处于分蘖期，想知道是否需要灌溉。
1. 调用 skill 时传入 crop_type="水稻", growth_stage="分蘖期", soil_moisture=55
2. 返回: {"success": true, "recommendation": {"should_irrigate": true, "water_amount": "每亩 40-50 立方米", "irrigation_method": "浅水勤灌", "best_time": "上午 9 点前或下午 4 点后", "reason": "分蘖期需水量大，土壤偏干"}, "notes": ["保持水层 2-3 厘米", "避免深水淹没"]}
```

## 注意事项
- 不同生长阶段作物需水量差异很大
- 会结合天气预报避免浇灌后下雨浪费水资源
- 建议优先采用节水灌溉方式
- 高温大风天气需要增加灌溉量