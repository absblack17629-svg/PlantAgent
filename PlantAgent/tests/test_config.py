# -*- coding: utf-8 -*-
"""
配置管理测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.config import ConfigManager, get_config_manager


def test_config_manager_singleton():
    """测试配置管理器单例模式"""
    manager1 = ConfigManager()
    manager2 = ConfigManager()
    manager3 = get_config_manager()
    
    assert manager1 is manager2
    assert manager2 is manager3
    print("✅ 配置管理器单例模式测试通过")


def test_config_loading():
    """测试配置加载"""
    manager = get_config_manager()
    
    assert manager.app is not None
    assert manager.llm is not None
    assert manager.yolo is not None
    assert manager.rag is not None
    assert manager.redis is not None
    assert manager.database is not None
    
    print("✅ 配置加载测试通过")


def test_config_validation():
    """测试配置验证"""
    manager = get_config_manager()
    
    is_valid = manager.validate()
    assert is_valid is True
    
    print("✅ 配置验证测试通过")


def test_config_properties():
    """测试配置属性访问"""
    manager = get_config_manager()
    
    # 测试应用配置
    assert manager.app.app_name == "YOLO11智能体系统"
    assert manager.app.app_version == "2.0.0"
    
    # 测试 LLM 配置
    assert manager.llm.max_tokens > 0
    assert 0.0 <= manager.llm.temperature <= 2.0
    
    # 测试 YOLO 配置
    assert manager.yolo.model_path is not None
    assert 0.0 <= manager.yolo.confidence_threshold <= 1.0
    
    # 测试 RAG 配置
    assert manager.rag.chunk_size > 0
    assert manager.rag.chunk_overlap >= 0
    assert manager.rag.chunk_overlap < manager.rag.chunk_size
    
    # 测试数据库配置
    assert manager.database.host is not None
    assert manager.database.port > 0
    assert manager.database.url.startswith("mysql+aiomysql://")
    
    # 测试 Redis 配置
    assert manager.redis.host is not None
    assert manager.redis.port > 0
    assert manager.redis.url.startswith("redis://")
    
    print("✅ 配置属性访问测试通过")


def test_config_get_method():
    """测试配置 get 方法"""
    manager = get_config_manager()
    
    # 测试点号路径访问
    assert manager.get("app_name") == "YOLO11智能体系统"
    assert manager.get("llm.max_tokens") > 0
    assert manager.get("yolo.confidence_threshold") >= 0.0
    assert manager.get("rag.offline_mode") in [True, False]
    
    # 测试默认值
    assert manager.get("non_existent_key", "default") == "default"
    assert manager.get("llm.non_existent", 100) == 100
    
    print("✅ 配置 get 方法测试通过")


def test_config_to_dict():
    """测试配置转字典"""
    manager = get_config_manager()
    
    config_dict = manager.to_dict()
    
    assert "app" in config_dict
    assert "llm" in config_dict
    assert "yolo" in config_dict
    assert "rag" in config_dict
    assert "database" in config_dict
    assert "redis" in config_dict
    
    assert config_dict["app"]["name"] == "YOLO11智能体系统"
    assert config_dict["yolo"]["model_path"] is not None
    
    print("✅ 配置转字典测试通过")


def test_database_url_generation():
    """测试数据库 URL 生成"""
    manager = get_config_manager()
    
    # 测试异步 URL
    async_url = manager.database.url
    assert "mysql+aiomysql://" in async_url
    assert manager.database.host in async_url
    assert str(manager.database.port) in async_url
    assert manager.database.database in async_url
    
    # 测试同步 URL
    sync_url = manager.database.sync_url
    assert "mysql+pymysql://" in sync_url
    
    print("✅ 数据库 URL 生成测试通过")


def test_redis_url_generation():
    """测试 Redis URL 生成"""
    manager = get_config_manager()
    
    redis_url = manager.redis.url
    assert "redis://" in redis_url
    assert manager.redis.host in redis_url
    assert str(manager.redis.port) in redis_url
    
    print("✅ Redis URL 生成测试通过")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 开始配置管理测试")
    print("="*60 + "\n")
    
    tests = [
        ("配置管理器单例模式", test_config_manager_singleton),
        ("配置加载", test_config_loading),
        ("配置验证", test_config_validation),
        ("配置属性访问", test_config_properties),
        ("配置 get 方法", test_config_get_method),
        ("配置转字典", test_config_to_dict),
        ("数据库 URL 生成", test_database_url_generation),
        ("Redis URL 生成", test_redis_url_generation),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name} 测试失败: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 测试总结: {passed} 通过, {failed} 失败")
    print("="*60)
