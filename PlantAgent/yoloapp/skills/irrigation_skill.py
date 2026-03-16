# -*- coding: utf-8 -*-
"""
智能灌溉技能
根据作物需求和天气情况提供灌溉建议
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class IrrigationSkill:
    """智能灌溉技能"""
    
    def __init__(self):
        self.name = "irrigation"
        self.description = "根据作物需求和天气情况提供灌溉建议"
        self.crop_water_requirements = self._init_water_requirements()
    
    def _init_water_requirements(self) -> Dict:
        """初始化作物需水数据"""
        return {
            "水稻": {
                "seedling": {"min_moisture": 80, "max_moisture": 100, "daily_water": 8},
                "tillering": {"min_moisture": 70, "max_moisture": 90, "daily_water": 10},
                "heading": {"min_moisture": 80, "max_moisture": 100, "daily_water": 12},
                "ripening": {"min_moisture": 60, "max_moisture": 80, "daily_water": 6}
            },
            "玉米": {
                "seedling": {"min_moisture": 60, "max_moisture": 75, "daily_water": 4},
                "jointing": {"min_moisture": 65, "max_moisture": 80, "daily_water": 6},
                "tasseling": {"min_moisture": 70, "max_moisture": 85, "daily_water": 8},
                "filling": {"min_moisture": 65, "max_moisture": 80, "daily_water": 7}
            },
            "小麦": {
                "seedling": {"min_moisture": 65, "max_moisture": 75, "daily_water": 3},
                "tillering": {"min_moisture": 60, "max_moisture": 75, "daily_water": 4},
                "jointing": {"min_moisture": 70, "max_moisture": 85, "daily_water": 6},
                "heading": {"min_moisture": 75, "max_moisture": 90, "daily_water": 7}
            },
            "大豆": {
                "seedling": {"min_moisture": 60, "max_moisture": 75, "daily_water": 3},
                "flowering": {"min_moisture": 65, "max_moisture": 80, "daily_water": 5},
                "pod_filling": {"min_moisture": 70, "max_moisture": 85, "daily_water": 6},
                "maturity": {"min_moisture": 55, "max_moisture": 70, "daily_water": 3}
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行灌溉决策
        
        Args:
            crop_type: 作物类型
            growth_stage: 生长阶段
            soil_moisture: 当前土壤湿度(%)
            weather_forecast: 天气预报数据（可选）
            last_irrigation: 上次灌溉时间（可选）
            
        Returns:
            灌溉建议
        """
        try:
            # 提取参数
            crop_type = kwargs.get('crop_type', '')
            growth_stage = kwargs.get('growth_stage', '')
            soil_moisture = kwargs.get('soil_moisture', 0)
            weather_forecast = kwargs.get('weather_forecast', {})
            last_irrigation = kwargs.get('last_irrigation', None)
            
            # 参数验证
            if not crop_type:
                return {"success": False, "error": "请提供作物类型"}
            if not growth_stage:
                return {"success": False, "error": "请提供生长阶段"}
            if soil_moisture < 0 or soil_moisture > 100:
                return {"success": False, "error": "土壤湿度应在0-100之间"}
            
            # 获取作物需水数据
            crop_data = self.crop_water_requirements.get(crop_type)
            if not crop_data:
                return {"success": False, "error": f"不支持的作物类型: {crop_type}"}
            
            stage_data = crop_data.get(growth_stage)
            if not stage_data:
                return {"success": False, "error": f"不支持的生长阶段: {growth_stage}"}
            
            # 分析是否需要灌溉
            irrigation_decision = self._make_irrigation_decision(
                soil_moisture=soil_moisture,
                stage_data=stage_data,
                weather_forecast=weather_forecast,
                last_irrigation=last_irrigation
            )
            
            # 构建输出
            output = {
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "current_soil_moisture": f"{soil_moisture}%",
                "optimal_moisture_range": f"{stage_data['min_moisture']}-{stage_data['max_moisture']}%",
                "need_irrigation": irrigation_decision["need_irrigation"],
                "irrigation_amount": irrigation_decision["irrigation_amount"],
                "irrigation_time": irrigation_decision["irrigation_time"],
                "reason": irrigation_decision["reason"],
                "next_check": irrigation_decision["next_check"],
                "additional_notes": irrigation_decision["notes"]
            }
            
            return {"success": True, "output": output}
            
        except Exception as e:
            return {"success": False, "error": f"灌溉决策失败: {str(e)}"}
    
    def _make_irrigation_decision(
        self,
        soil_moisture: float,
        stage_data: Dict,
        weather_forecast: Dict,
        last_irrigation: str = None
    ) -> Dict:
        """做出灌溉决策"""
        min_moisture = stage_data["min_moisture"]
        max_moisture = stage_data["max_moisture"]
        daily_water = stage_data["daily_water"]
        
        # 分析未来降雨
        future_rain = self._analyze_future_rain(weather_forecast)
        
        # 决策逻辑
        need_irrigation = False
        irrigation_amount = "0mm"
        irrigation_time = "无需灌溉"
        reason = ""
        next_check = "2天后"
        notes = []
        
        # 情况1: 土壤湿度低于最低要求
        if soil_moisture < min_moisture:
            need_irrigation = True
            deficit = max_moisture - soil_moisture
            irrigation_amount = f"{int(deficit * 0.8)}mm"
            irrigation_time = "早晨6-8点或傍晚5-7点"
            reason = f"土壤湿度({soil_moisture}%)低于最低要求({min_moisture}%)"
            next_check = "1天后"
            
            if future_rain > 10:
                notes.append("[WARN] 未来有降雨预报，可适当减少灌溉量")
                irrigation_amount = f"{int(deficit * 0.5)}mm"
        
        # 情况2: 土壤湿度在适宜范围内
        elif min_moisture <= soil_moisture <= max_moisture:
            need_irrigation = False
            reason = f"土壤湿度({soil_moisture}%)在适宜范围内"
            
            if future_rain < 5:
                notes.append("[WATER] 未来无降雨，2天后需检查土壤湿度")
                next_check = "2天后"
            else:
                notes.append("🌧️ 未来有降雨，暂无需灌溉")
                next_check = "3天后"
        
        # 情况3: 土壤湿度过高
        else:
            need_irrigation = False
            reason = f"土壤湿度({soil_moisture}%)过高，需要排水"
            notes.append("[WARN] 注意排水，防止涝害")
            next_check = "1天后"
        
        # 考虑上次灌溉时间
        if last_irrigation:
            try:
                last_time = datetime.fromisoformat(last_irrigation)
                days_since = (datetime.now() - last_time).days
                if days_since < 1 and need_irrigation:
                    notes.append("ℹ️ 距上次灌溉不足1天，建议再观察")
            except:
                pass
        
        # 灌溉方式建议
        if need_irrigation:
            notes.append("[INFO] 建议采用滴灌或喷灌，节水高效")
            notes.append("🌡️ 避免高温时段灌溉，减少蒸发损失")
        
        return {
            "need_irrigation": need_irrigation,
            "irrigation_amount": irrigation_amount,
            "irrigation_time": irrigation_time,
            "reason": reason,
            "next_check": next_check,
            "notes": notes
        }
    
    def _analyze_future_rain(self, weather_forecast: Dict) -> float:
        """分析未来降雨量"""
        if not weather_forecast or "forecast" not in weather_forecast:
            return 0
        
        total_rain = 0
        forecast = weather_forecast.get("forecast", [])
        
        # 统计未来3天降雨
        for day in forecast[:3]:
            precip = day.get("precip", "0")
            try:
                total_rain += float(precip)
            except (ValueError, TypeError):
                pass
        
        return total_rain
