# Skill: 天气查询 (Weather Query)

## 描述
查询指定地区当前天气和未来7天预报，提供农业相关的生产建议。

## 参数
- `location` (必填): 要查询的地区/城市名称
- `days` (可选): 预报天数，默认为 7，最多为 7

## 返回值格式
返回 JSON 格式的天气信息，包含:
- `success`: 是否成功获取天气 (boolean)
- `current`: 当前天气状况:
  - `temperature`: 当前温度 (string, 如 "20°C")
  - `condition`: 天气状况 (string, 如 "晴")
  - `humidity`: 湿度 (string, 如 "65%")
  - `wind`: 风力风向 (string, 如 "东南风 3级")
  - `aqi`: 空气质量指数 (number)
- `forecast`: 未来几天预报数组，每个元素包含:
  - `date`: 日期 (string)
  - `temperature_high`: 最高温度 (string)
  - `temperature_low`: 最低温度 (string)
  - `condition`: 天气状况 (string)
  - `wind`: 风力 (string)
- `advice`: 农业建议数组 (array)

## 使用示例
```
用户想知道南京的天气情况。
1. 调用 skill 时传入 location="南京"
2. 返回: {"success": true, "current": {"temperature": "22°C", "condition": "晴", "humidity": "60%", ...}, "forecast": [...], "advice": ["适合喷施农药", "注意灌溉"]}
```

## 注意事项
- 天气数据来自气象 API，有缓存机制（1小时内重复查询返回缓存）
- 农业建议会根据天气状况自动生成
- 极端天气（暴雨、台风等）会给出特别提醒
- 如果 API 不可用，会返回模拟数据但会标注