# -*- coding: utf-8 -*-
"""
种植规划技能
根据土地情况和季节提供种植规划建议
"""

from typing import Dict, Any, List


class PlantingPlanSkill:
    """种植规划技能"""
    
    def __init__(self):
        self.name = "planting_plan"
        self.description = "根据土地情况和季节提供种植规划建议"
        self.crop_database = self._init_crop_database()
    
    def _init_crop_database(self) -> Dict:
        """初始化作物数据库"""
        return {
            "水稻": {
                "seasons": ["春季", "夏季"],
                "soil_types": ["壤土", "黏土", "水田"],
                "density": "每亩30000-35000株",
                "yield": "每亩500-700公斤",
                "growth_period": "120-150天",
                "notes": ["需要充足水源", "注意防治稻瘟病", "适时施肥"]
            },
            "玉米": {
                "seasons": ["春季", "夏季"],
                "soil_types": ["壤土", "砂壤土"],
                "density": "每亩3500-4500株",
                "yield": "每亩400-600公斤",
                "growth_period": "90-120天",
                "notes": ["耐旱性强", "注意防治玉米螟", "需要充足阳光"]
            },
            "小麦": {
                "seasons": ["秋季", "冬季"],
                "soil_types": ["壤土", "砂壤土"],
                "density": "每亩25000-30000株",
                "yield": "每亩350-500公斤",
                "growth_period": "200-230天",
                "notes": ["耐寒性强", "注意防治赤霉病", "适时灌溉"]
            },
            "大豆": {
                "seasons": ["春季", "夏季"],
                "soil_types": ["壤土", "砂壤土"],
                "density": "每亩12000-15000株",
                "yield": "每亩150-250公斤",
                "growth_period": "100-130天",
                "notes": ["固氮作物", "适合轮作", "注意防治病虫害"]
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行种植规划
        
        Args:
            land_area: 土地面积（亩）
            soil_type: 土壤类型
            location: 地理位置
            season: 季节
            
        Returns:
            种植规划建议
        """
        try:
            # 提取参数
            land_area = kwargs.get('land_area', 0)
            soil_type = kwargs.get('soil_type', '壤土')
            location = kwargs.get('location', '')
            season = kwargs.get('season', '春季')
            
            # 参数验证
            if land_area <= 0:
                return {"success": False, "error": "土地面积必须大于0"}
            
            # 推荐作物
            recommended_crops = self._recommend_crops(soil_type, season)
            
            if not recommended_crops:
                return {"success": False, "error": f"未找到适合{season}和{soil_type}的作物"}
            
            # 生成详细规划
            detailed_plan = await self._generate_detailed_plan(
                land_area=land_area,
                soil_type=soil_type,
                location=location,
                season=season,
                recommended_crops=recommended_crops
            )
            
            # 构建输出
            output = {
                "recommended_crops": [crop["name"] for crop in recommended_crops],
                "land_area": f"{land_area}亩",
                "soil_type": soil_type,
                "season": season,
                "location": location,
                "crop_details": recommended_crops,
                "detailed_plan": detailed_plan
            }
            
            return {"success": True, "output": output}
            
        except Exception as e:
            return {"success": False, "error": f"种植规划失败: {str(e)}"}
    
    def _recommend_crops(self, soil_type: str, season: str) -> list:
        """推荐适合的作物"""
        recommended = []
        
        for crop_name, crop_info in self.crop_database.items():
            # 检查季节匹配
            if season in crop_info["seasons"]:
                # 检查土壤类型匹配
                if soil_type in crop_info["soil_types"]:
                    recommended.append({
                        "name": crop_name,
                        "density": crop_info["density"],
                        "yield": crop_info["yield"],
                        "growth_period": crop_info["growth_period"],
                        "notes": crop_info["notes"]
                    })
        
        return recommended
    
    async def _generate_detailed_plan(
        self,
        land_area: float,
        soil_type: str,
        location: str,
        season: str,
        recommended_crops: list
    ) -> str:
        """生成详细的种植规划"""
        plan_parts = []
        
        # 基本信息
        plan_parts.append(f"## 种植规划方案\n")
        plan_parts.append(f"**地块信息**: {location} {land_area}亩 {soil_type}")
        plan_parts.append(f"**种植季节**: {season}\n")
        
        # 推荐作物详情
        plan_parts.append(f"## 推荐作物\n")
        for i, crop in enumerate(recommended_crops, 1):
            plan_parts.append(f"### {i}. {crop['name']}")
            plan_parts.append(f"- **种植密度**: {crop['density']}")
            plan_parts.append(f"- **预期产量**: {crop['yield']}")
            plan_parts.append(f"- **生长周期**: {crop['growth_period']}")
            plan_parts.append(f"- **注意事项**:")
            for note in crop['notes']:
                plan_parts.append(f"  - {note}")
            plan_parts.append("")
        
        # 种植建议
        plan_parts.append(f"## 种植建议\n")
        plan_parts.append(f"1. **土地准备**: 提前15-20天进行深耕，施足基肥")
        plan_parts.append(f"2. **种子选择**: 选择适合{location}气候的优质品种")
        plan_parts.append(f"3. **播种时间**: 根据{season}气温选择最佳播种期")
        plan_parts.append(f"4. **田间管理**: 及时除草、施肥、灌溉")
        plan_parts.append(f"5. **病虫害防治**: 预防为主，综合防治")
        
        # 轮作建议
        if len(recommended_crops) > 1:
            plan_parts.append(f"\n## 轮作建议\n")
            plan_parts.append(f"建议采用轮作制度，避免连作障碍：")
            crop_names = [c['name'] for c in recommended_crops]
            plan_parts.append(f"- 可轮作作物: {' → '.join(crop_names)}")
        
        return "\n".join(plan_parts)
