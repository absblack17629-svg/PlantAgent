# -*- coding: utf-8 -*-
"""
缓存服务
用于缓存检测结果和其他计算密集型操作的结果
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    """缓存服务类"""
    
    def __init__(self, cache_dir: str = "./cache", ttl_minutes: int = 60):
        """
        初始化缓存服务
        
        Args:
            cache_dir: 缓存目录
            ttl_minutes: 缓存过期时间（分钟）
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(minutes=ttl_minutes)
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"[OK] 缓存服务初始化成功，缓存目录: {cache_dir}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        计算文件的MD5哈希值
        
        Args:
            file_path: 文件路径
        
        Returns:
            MD5哈希值
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"计算文件哈希失败: {str(e)}")
            return None
    
    def _get_cache_key(self, operation: str, file_path: str) -> str:
        """
        生成缓存键
        
        Args:
            operation: 操作类型（如 'detection'）
            file_path: 文件路径
        
        Returns:
            缓存键
        """
        file_hash = self._get_file_hash(file_path)
        if not file_hash:
            return None
        return f"{operation}_{file_hash}"
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, operation: str, file_path: str) -> Optional[Any]:
        """
        获取缓存结果
        
        Args:
            operation: 操作类型
            file_path: 文件路径
        
        Returns:
            缓存的结果，如果不存在或过期则返回None
        """
        try:
            cache_key = self._get_cache_key(operation, file_path)
            if not cache_key:
                return None
            
            cache_file = self._get_cache_file_path(cache_key)
            
            # 检查缓存文件是否存在
            if not os.path.exists(cache_file):
                return None
            
            # 读取缓存
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 检查是否过期
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.info(f"缓存已过期: {cache_key}")
                os.remove(cache_file)
                return None
            
            logger.info(f"[OK] 命中缓存: {cache_key}")
            return cache_data['result']
        
        except Exception as e:
            logger.error(f"读取缓存失败: {str(e)}")
            return None
    
    def set(self, operation: str, file_path: str, result: Any) -> bool:
        """
        设置缓存
        
        Args:
            operation: 操作类型
            file_path: 文件路径
            result: 要缓存的结果
        
        Returns:
            是否成功
        """
        try:
            cache_key = self._get_cache_key(operation, file_path)
            if not cache_key:
                return False
            
            cache_file = self._get_cache_file_path(cache_key)
            
            # 保存缓存
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'file_path': file_path,
                'result': result
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[OK] 缓存已保存: {cache_key}")
            return True
        
        except Exception as e:
            logger.error(f"保存缓存失败: {str(e)}")
            return False
    
    def clear(self, operation: str = None) -> int:
        """
        清理缓存
        
        Args:
            operation: 操作类型，如果为None则清理所有缓存
        
        Returns:
            清理的文件数量
        """
        try:
            count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    if operation is None or filename.startswith(f"{operation}_"):
                        file_path = os.path.join(self.cache_dir, filename)
                        os.remove(file_path)
                        count += 1
            
            logger.info(f"[OK] 已清理 {count} 个缓存文件")
            return count
        
        except Exception as e:
            logger.error(f"清理缓存失败: {str(e)}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f))
                for f in cache_files
            )
            
            return {
                'cache_dir': self.cache_dir,
                'total_files': len(cache_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'ttl_minutes': self.ttl.total_seconds() / 60
            }
        
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
            return {}


# 全局缓存服务实例
_cache_service_instance = None


def get_cache_service() -> CacheService:
    """获取缓存服务单例"""
    global _cache_service_instance
    if _cache_service_instance is None:
        _cache_service_instance = CacheService()
    return _cache_service_instance
