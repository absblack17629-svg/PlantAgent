#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加测试新闻数据
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import AsyncSessionLocal
from crud.news import crud_news
from schemas.news import NewsCreate


async def add_test_news():
    """添加测试新闻数据"""
    
    test_news = [
        {
            "title": "智慧农业：AI技术助力精准种植",
            "summary": "人工智能技术正在改变传统农业，通过图像识别和数据分析，帮助农民实现精准种植，提高作物产量。",
            "content": "随着人工智能技术的发展，智慧农业正在成为现代农业的重要发展方向。通过AI图像识别技术，可以实时监测作物生长状态，及时发现病虫害，为农民提供科学的种植建议。",
            "category": "科技农业",
            "author": "农业科技日报",
            "source": "农业科技网",
            "is_published": True
        },
        {
            "title": "无人机植保技术在水稻种植中的应用",
            "summary": "无人机植保技术以其高效、精准的特点，在水稻种植中得到广泛应用，大大提高了农业生产效率。",
            "content": "无人机植保技术通过精准喷洒农药，不仅提高了作业效率，还减少了农药使用量，降低了环境污染。在水稻种植中，无人机可以快速完成大面积的植保作业。",
            "category": "植保技术",
            "author": "现代农业",
            "source": "农业机械化",
            "is_published": True
        },
        {
            "title": "温室大棚智能控制系统助力蔬菜种植",
            "summary": "智能温室大棚通过自动化控制系统，实现温度、湿度、光照的精准调控，为蔬菜生长创造最佳环境。",
            "content": "现代温室大棚配备了先进的智能控制系统，可以根据作物生长需求自动调节环境参数。通过传感器实时监测，系统能够精准控制温度、湿度、光照等因素，确保蔬菜在最佳环境中生长。",
            "category": "设施农业",
            "author": "设施农业研究",
            "source": "农业工程学报",
            "is_published": True
        },
        {
            "title": "有机农业：回归自然的种植方式",
            "summary": "有机农业强调不使用化学农药和化肥，通过生态循环的方式种植，生产出健康安全的农产品。",
            "content": "有机农业是一种可持续的农业生产方式，通过合理轮作、生物防治等手段，在不使用化学农药的情况下，生产出高品质的农产品。这种种植方式不仅保护了环境，也为消费者提供了更健康的食品选择。",
            "category": "有机农业",
            "author": "绿色农业",
            "source": "有机农业杂志",
            "is_published": True
        },
        {
            "title": "物联网技术在畜牧业中的创新应用",
            "summary": "物联网技术通过智能传感器和数据分析，实现畜牧业的精准管理，提高养殖效率和动物福利。",
            "content": "物联网技术在畜牧业中的应用越来越广泛。通过安装智能传感器，可以实时监测动物的健康状况、饲料消耗、环境参数等信息。大数据分析帮助养殖户做出更科学的决策，提高养殖效益。",
            "category": "畜牧养殖",
            "author": "畜牧科技",
            "source": "中国畜牧兽医报",
            "is_published": True
        },
        {
            "title": "节水灌溉技术推广助力农业可持续发展",
            "summary": "滴灌、喷灌等节水灌溉技术的推广，有效提高了水资源利用效率，为农业可持续发展提供了保障。",
            "content": "在水资源日益紧张的背景下，节水灌溉技术显得尤为重要。滴灌技术可以将水分直接输送到作物根部，大大减少了水分蒸发和浪费。这种技术不仅节约了水资源，还提高了作物产量。",
            "category": "节水农业",
            "author": "水利农业",
            "source": "农业水利工程",
            "is_published": True
        },
        {
            "title": "农产品质量安全追溯体系建设",
            "summary": "建立完善的农产品质量安全追溯体系，让消费者能够了解农产品从田间到餐桌的全过程。",
            "content": "农产品质量安全追溯体系通过二维码、RFID等技术，记录农产品生产、加工、流通的全过程信息。消费者扫码即可查看产品来源、生产过程、检测结果等信息，确保食品安全。",
            "category": "质量安全",
            "author": "食品安全",
            "source": "农产品质量与安全",
            "is_published": True
        },
        {
            "title": "农村电商助力农产品销售",
            "summary": "电商平台为农产品打开了更广阔的销售渠道，帮助农民增收致富，推动乡村振兴。",
            "content": "随着互联网的普及，农村电商快速发展。通过电商平台，农民可以直接将农产品销售给消费者，减少了中间环节，提高了收益。同时，电商也为特色农产品提供了展示平台。",
            "category": "农村电商",
            "author": "电商农业",
            "source": "农村电商研究",
            "is_published": True
        },
        {
            "title": "生物防治技术在病虫害防控中的应用",
            "summary": "利用天敌昆虫、微生物等生物防治手段，减少化学农药使用，实现绿色防控。",
            "content": "生物防治是一种环保的病虫害防控方式。通过释放天敌昆虫、使用生物农药等手段，可以有效控制害虫数量，同时不会对环境造成污染。这种方法越来越受到农民的欢迎。",
            "category": "病虫害防治",
            "author": "植保科技",
            "source": "植物保护学报",
            "is_published": True
        },
        {
            "title": "农业机械化水平持续提升",
            "summary": "现代农业机械的推广应用，大大提高了农业生产效率，解放了农村劳动力。",
            "content": "农业机械化是现代农业的重要标志。从耕地、播种到收获，各个环节都实现了机械化作业。大型农机的使用不仅提高了效率，还降低了劳动强度，让农业生产更加轻松高效。",
            "category": "农业机械",
            "author": "农机推广",
            "source": "农业机械学报",
            "is_published": True
        }
    ]
    
    async with AsyncSessionLocal() as db:
        print("开始添加测试新闻数据...")
        
        for news_data in test_news:
            try:
                news_in = NewsCreate(**news_data)
                news = await crud_news.create(db, news_in)
                print(f"✅ 添加新闻: {news.title}")
            except Exception as e:
                print(f"❌ 添加失败: {news_data['title']} - {str(e)}")
        
        print(f"\n完成！共添加 {len(test_news)} 条新闻")


if __name__ == "__main__":
    asyncio.run(add_test_news())
