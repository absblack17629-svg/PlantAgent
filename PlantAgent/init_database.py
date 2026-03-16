# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建数据库、表结构并插入农业相关的示例数据
"""

import asyncio
import pymysql
from datetime import datetime
from config import settings
from config.db_conf import engine, Base
from models import User, News, DetectionLog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import hashlib


def hash_password(password: str) -> str:
    """简单的密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_database():
    """创建数据库（如果不存在）"""
    try:
        # 连接MySQL（不指定数据库）
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"✅ 数据库 '{settings.MYSQL_DATABASE}' 创建成功")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False


async def create_tables():
    """创建所有表"""
    try:
        async with engine.begin() as conn:
            # 删除所有表（可选，用于重新初始化）
            # await conn.run_sync(Base.metadata.drop_all)
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ 数据表创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据表失败: {e}")
        return False


async def insert_sample_data():
    """插入示例数据"""
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. 创建测试用户
            test_user = User(
                username="admin",
                email="admin@yolo11.com",
                hashed_password=hash_password("admin123"),
                nickname="系统管理员",
                is_active=True,
                is_superuser=True
            )
            session.add(test_user)
            
            # 2. 插入农业相关新闻
            agriculture_news = [
                {
                    "title": "智能农业：AI技术助力精准种植",
                    "summary": "人工智能技术正在改变传统农业，通过图像识别和数据分析，农民可以更精准地管理作物，提高产量并减少资源浪费。",
                    "content": """
                    随着人工智能技术的快速发展，智能农业正在成为现代农业的重要发展方向。通过部署YOLO等先进的目标检测算法，
                    农民可以实时监测作物生长状况，及时发现病虫害，并采取针对性的防治措施。
                    
                    智能农业系统可以：
                    1. 自动识别作物病虫害，准确率达95%以上
                    2. 监测作物生长状态，优化灌溉和施肥方案
                    3. 预测产量，帮助农民做好市场规划
                    4. 减少农药使用，实现绿色环保种植
                    
                    这项技术已在多个省份试点应用，取得了显著成效。
                    """,
                    "category": "technology",
                    "author": "农业科技日报",
                    "source": "农业科技网",
                    "tags": '["智能农业", "AI", "精准种植", "病虫害识别"]',
                    "view_count": 1520,
                    "like_count": 89,
                    "comment_count": 23,
                    "is_published": 1
                },
                {
                    "title": "无人机植保技术在水稻种植中的应用",
                    "summary": "无人机植保技术凭借其高效、精准的特点，正在水稻种植领域得到广泛应用，大幅提升了植保效率。",
                    "content": """
                    无人机植保技术是现代农业的重要创新。相比传统人工喷洒，无人机植保具有以下优势：
                    
                    1. 效率高：每小时可作业60-80亩，是人工的30-40倍
                    2. 精准度高：通过GPS定位和智能控制，实现精准喷洒
                    3. 安全性好：避免农药对操作人员的伤害
                    4. 节约资源：农药利用率提高30%以上
                    
                    目前，无人机植保已在全国多个水稻主产区推广应用，受到农民的广泛欢迎。
                    """,
                    "category": "technology",
                    "author": "现代农业",
                    "source": "农业机械化",
                    "tags": '["无人机", "植保", "水稻", "智能农机"]',
                    "view_count": 980,
                    "like_count": 56,
                    "comment_count": 15,
                    "is_published": 1
                },
                {
                    "title": "温室大棚智能监控系统助力蔬菜种植",
                    "summary": "智能监控系统通过传感器和AI算法，实时监测温室环境，自动调节温度、湿度和光照，为蔬菜生长创造最佳条件。",
                    "content": """
                    温室大棚智能监控系统是设施农业的重要组成部分。该系统集成了多种传感器和智能控制设备：
                    
                    核心功能：
                    1. 环境监测：实时监测温度、湿度、光照、CO2浓度等参数
                    2. 自动控制：根据作物需求自动调节通风、遮阳、灌溉等
                    3. 病害预警：通过图像识别技术及早发现病虫害
                    4. 数据分析：积累种植数据，优化种植方案
                    
                    应用效果：
                    - 蔬菜产量提升20-30%
                    - 能源消耗降低15-25%
                    - 人工成本减少40%以上
                    
                    该技术已在山东、河北等地的蔬菜基地广泛应用。
                    """,
                    "category": "technology",
                    "author": "设施农业研究所",
                    "source": "中国农业网",
                    "tags": '["温室大棚", "智能监控", "蔬菜种植", "物联网"]',
                    "view_count": 1230,
                    "like_count": 72,
                    "comment_count": 19,
                    "is_published": 1
                },
                {
                    "title": "果园智能管理：从种植到采摘的全程数字化",
                    "summary": "现代果园通过部署智能管理系统，实现了从种植、管理到采摘的全程数字化，大幅提升了果园管理效率和果品质量。",
                    "content": """
                    智能果园管理系统整合了多项先进技术，为果农提供全方位的数字化解决方案：
                    
                    系统特点：
                    1. 生长监测：通过图像识别技术监测果树生长状况
                    2. 病虫害防治：AI识别病虫害，推荐精准防治方案
                    3. 成熟度判断：自动判断果实成熟度，指导采摘时机
                    4. 产量预测：基于历史数据和当前状况预测产量
                    5. 溯源管理：建立果品质量追溯体系
                    
                    应用案例：
                    某苹果种植基地应用该系统后，优质果率提升25%，管理成本降低30%，
                    果品售价提高20%，经济效益显著提升。
                    
                    智能果园管理代表了现代农业的发展方向。
                    """,
                    "category": "technology",
                    "author": "果树研究中心",
                    "source": "果业科技",
                    "tags": '["智能果园", "数字化", "果树管理", "AI识别"]',
                    "view_count": 1450,
                    "like_count": 95,
                    "comment_count": 28,
                    "is_published": 1
                },
                {
                    "title": "土壤检测技术：科学施肥的基础",
                    "summary": "现代土壤检测技术能够快速准确地分析土壤成分，为科学施肥提供数据支持，实现精准农业。",
                    "content": """
                    土壤检测是精准农业的重要环节。现代土壤检测技术包括：
                    
                    检测内容：
                    1. 土壤养分：氮、磷、钾及微量元素含量
                    2. 土壤pH值：影响养分有效性的关键指标
                    3. 有机质含量：反映土壤肥力水平
                    4. 土壤质地：影响保水保肥能力
                    
                    技术优势：
                    - 快速检测：30分钟内出结果
                    - 精准分析：误差控制在5%以内
                    - 智能推荐：自动生成施肥方案
                    
                    应用效果：
                    通过科学施肥，可以减少化肥使用量20-30%，同时提高作物产量10-15%，
                    既保护了环境，又提高了经济效益。
                    
                    建议农民每年至少进行一次土壤检测。
                    """,
                    "category": "technology",
                    "author": "土壤研究所",
                    "source": "农业科学",
                    "tags": '["土壤检测", "科学施肥", "精准农业", "环保"]',
                    "view_count": 890,
                    "like_count": 48,
                    "comment_count": 12,
                    "is_published": 1
                },
                {
                    "title": "农产品质量安全追溯系统建设进展",
                    "summary": "全国农产品质量安全追溯系统建设取得重要进展，消费者可以通过扫码了解农产品从田间到餐桌的全过程。",
                    "content": """
                    农产品质量安全追溯系统是保障食品安全的重要手段。系统建设进展：
                    
                    系统功能：
                    1. 生产记录：记录种植、施肥、用药等全过程
                    2. 流通追踪：记录运输、仓储、销售等环节
                    3. 质量检测：上传产品检测报告
                    4. 信息查询：消费者扫码即可查看全部信息
                    
                    建设成果：
                    - 已覆盖全国80%的规模化种植基地
                    - 接入产品超过10万种
                    - 日查询量突破100万次
                    
                    社会效益：
                    追溯系统的建设增强了消费者信心，促进了优质农产品销售，
                    倒逼生产者提高产品质量，形成了良性循环。
                    
                    未来将继续扩大覆盖范围，提升系统功能。
                    """,
                    "category": "other",
                    "author": "农业农村部",
                    "source": "中国农业新闻网",
                    "tags": '["质量追溯", "食品安全", "农产品", "区块链"]',
                    "view_count": 2100,
                    "like_count": 128,
                    "comment_count": 45,
                    "is_published": 1
                }
            ]
            
            for news_data in agriculture_news:
                news = News(**news_data)
                session.add(news)
            
            # 提交所有数据
            await session.commit()
            print("✅ 示例数据插入成功")
            print(f"   - 创建用户: admin (密码: admin123)")
            print(f"   - 插入新闻: {len(agriculture_news)} 条农业相关新闻")
            
            return True
            
        except Exception as e:
            await session.rollback()
            print(f"❌ 插入示例数据失败: {e}")
            return False


async def main():
    """主函数"""
    print("=" * 50)
    print("  YOLO11智能体系统 - 数据库初始化")
    print("=" * 50)
    print()
    
    # 1. 创建数据库
    print("[1/3] 创建数据库...")
    if not create_database():
        print("数据库创建失败，请检查MySQL配置")
        return
    print()
    
    # 2. 创建表结构
    print("[2/3] 创建数据表...")
    if not await create_tables():
        print("数据表创建失败")
        return
    print()
    
    # 3. 插入示例数据
    print("[3/3] 插入示例数据...")
    if not await insert_sample_data():
        print("示例数据插入失败")
        return
    print()
    
    print("=" * 50)
    print("  ✅ 数据库初始化完成！")
    print("=" * 50)
    print()
    print("📝 数据库信息:")
    print(f"   主机: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"   数据库: {settings.MYSQL_DATABASE}")
    print(f"   用户: {settings.MYSQL_USER}")
    print()
    print("👤 测试账号:")
    print("   用户名: admin")
    print("   密码: admin123")
    print()
    print("🌐 访问地址:")
    print(f"   首页: http://localhost:{settings.PORT}")
    print(f"   API文档: http://localhost:{settings.PORT}/docs")
    print()


if __name__ == "__main__":
    asyncio.run(main())
