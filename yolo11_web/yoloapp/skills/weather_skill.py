# -*- coding: utf-8 -*-
"""
天气监测技能
获取天气信息并提供农业建议
"""

from typing import Dict, Any, Optional, List
import requests
from datetime import datetime, timedelta


class WeatherSkill:
    """天气监测技能"""
    
    def __init__(self):
        self.name = "weather"
        self.description = "获取天气信息并提供农业建议"
        
        # 尝试从settings获取配置
        try:
            from config.settings import settings
            self.api_key = settings.weather_api_key if hasattr(settings, 'weather_api_key') else ""
            self.provider = settings.weather_api_provider if hasattr(settings, 'weather_api_provider') else "qweather"
        except:
            self.api_key = ""
            self.provider = "qweather"
        
        self.cache = {}  # 简单的内存缓存
        self.cache_duration = 3600  # 缓存1小时
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行天气查询
        
        Args:
            location: 城市名或经纬度
            
        Returns:
            天气信息和农业建议
        """
        try:
            location = kwargs.get('location', '')
            
            if not location:
                return {"success": False, "error": "请提供地理位置"}
            
            # 检查缓存
            cache_key = f"{location}_{self.provider}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_duration:
                    return {"success": True, "output": cached_data}
            
            # 获取天气数据
            if self.api_key:
                weather_data = await self._fetch_weather_from_api(location)
            else:
                # 如果没有API Key，返回模拟数据
                weather_data = self._get_mock_weather_data(location)
            
            # 生成农业建议
            agricultural_advice = self._generate_agricultural_advice(weather_data)
            
            # 构建输出
            output = {
                "location": location,
                "current": weather_data["current"],
                "forecast": weather_data["forecast"],
                "agricultural_advice": agricultural_advice,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 更新缓存
            self.cache[cache_key] = (output, datetime.now())
            
            return {"success": True, "output": output}
            
        except Exception as e:
            return {"success": False, "error": f"天气查询失败: {str(e)}"}
    
    async def _fetch_weather_from_api(self, location: str) -> Dict:
        """从API获取天气数据"""
        if self.provider == "qweather":
            return await self._fetch_from_qweather(location)
        else:
            return self._get_mock_weather_data(location)
    
    async def _fetch_from_qweather(self, location: str) -> Dict:
        """从和风天气API获取数据"""
        try:
            # 和风天气API调用示例
            base_url = "https://devapi.qweather.com/v7"
            
            # 获取当前天气
            current_url = f"{base_url}/weather/now"
            current_params = {
                "location": location,
                "key": self.api_key
            }
            current_response = requests.get(current_url, params=current_params, timeout=5)
            current_data = current_response.json()
            
            # 获取7天预报
            forecast_url = f"{base_url}/weather/7d"
            forecast_params = {
                "location": location,
                "key": self.api_key
            }
            forecast_response = requests.get(forecast_url, params=forecast_params, timeout=5)
            forecast_data = forecast_response.json()
            
            # 解析数据
            return self._parse_qweather_data(current_data, forecast_data)
            
        except Exception as e:
            print(f"和风天气API调用失败: {str(e)}")
            return self._get_mock_weather_data(location)
    
    def _parse_qweather_data(self, current_data: Dict, forecast_data: Dict) -> Dict:
        """解析和风天气数据"""
        current = {
            "temp": current_data.get("now", {}).get("temp", "N/A"),
            "humidity": current_data.get("now", {}).get("humidity", "N/A"),
            "weather": current_data.get("now", {}).get("text", "N/A"),
            "wind_speed": current_data.get("now", {}).get("windSpeed", "N/A"),
            "pressure": current_data.get("now", {}).get("pressure", "N/A")
        }
        
        forecast = []
        for day in forecast_data.get("daily", [])[:7]:
            forecast.append({
                "date": day.get("fxDate", ""),
                "temp_max": day.get("tempMax", ""),
                "temp_min": day.get("tempMin", ""),
                "weather": day.get("textDay", ""),
                "humidity": day.get("humidity", ""),
                "precip": day.get("precip", "0")
            })
        
        return {"current": current, "forecast": forecast}
    
    def _get_mock_weather_data(self, location: str) -> Dict:
        """获取模拟天气数据（用于测试）"""
        current = {
            "temp": "25",
            "humidity": "70",
            "weather": "多云",
            "wind_speed": "3",
            "pressure": "1013"
        }
        
        forecast = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            forecast.append({
                "date": date,
                "temp_max": str(26 + i % 3),
                "temp_min": str(18 + i % 3),
                "weather": ["晴", "多云", "阴", "小雨"][i % 4],
                "humidity": str(65 + i * 2),
                "precip": str(i * 2) if i % 3 == 0 else "0"
            })
        
        return {"current": current, "forecast": forecast}
    
    def _generate_agricultural_advice(self, weather_data: Dict) -> str:
        """根据天气生成农业建议"""
        current = weather_data["current"]
        forecast = weather_data["forecast"]
        
        advice_parts = []
        
        # 当前天气建议
        temp = float(current.get("temp", 25))
        humidity = float(current.get("humidity", 70))
        
        if temp > 30:
            advice_parts.append("[WARN] 高温天气，建议增加灌溉频率，避免中午时段作业")
        elif temp < 10:
            advice_parts.append("[WARN] 低温天气，注意防寒保暖，延迟播种时间")
        
        if humidity > 80:
            advice_parts.append("[WARN] 湿度较高，注意防治病害，加强通风")
        elif humidity < 40:
            advice_parts.append("[WATER] 湿度较低，适当增加灌溉，保持土壤湿润")
        
        # 未来天气建议
        rain_days = sum(1 for day in forecast if float(day.get("precip", 0)) > 5)
        if rain_days >= 3:
            advice_parts.append("🌧️ 未来多雨天气，暂缓灌溉，注意排水防涝")
        elif rain_days == 0:
            advice_parts.append("☀️ 未来无降雨，做好灌溉准备")
        
        # 农事建议
        if 20 <= temp <= 28 and 50 <= humidity <= 75:
            advice_parts.append("[OK] 天气条件良好，适合进行田间作业和施肥")
        
        return "\n".join(advice_parts) if advice_parts else "天气条件正常，按常规管理即可"
