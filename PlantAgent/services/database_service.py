# -*- coding: utf-8 -*-
"""
数据库服务 - 异步版本
负责MySQL和Redis数据库的异步操作
"""

import time
from datetime import datetime
from typing import List, Dict, Optional
import aiomysql
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

import config
from config.db_conf import AsyncSessionLocal


class DatabaseService:
    """数据库服务类 - 异步版本"""

    def __init__(self):
        self.mysql_pool = None
        self.redis_client = None
        self._initialized = False

    async def init_databases(self):
        """异步初始化数据库连接"""
        if self._initialized:
            return
        
        self.mysql_pool = await self._init_mysql()
        self.redis_client = await self._init_redis()
        self._initialized = True

    async def _init_mysql(self) -> Optional[aiomysql.Pool]:
        """
        异步初始化MySQL数据库连接池

        Returns:
            MySQL连接池对象或None
        """
        try:
            # 1. 基础配置
            basic_config = {
                "host": config.MYSQL_CONFIG.get("host"),
                "port": config.MYSQL_CONFIG.get("port", 3306),
                "user": config.MYSQL_CONFIG.get("user"),
                "password": config.MYSQL_CONFIG.get("password"),
                "charset": config.MYSQL_CONFIG.get("charset", "utf8mb4"),
                "connect_timeout": 10
            }
            if not all([basic_config["host"], basic_config["user"], basic_config["port"]]):
                print("[WARN] MySQL基础配置不完整，跳过MySQL初始化")
                return None

            # 2. 创建数据库（如果不存在）
            temp_conn = await aiomysql.connect(**basic_config)
            db_name = config.MYSQL_CONFIG["database"]
            create_db_sql = f"CREATE DATABASE IF NOT EXISTS {db_name} DEFAULT CHARACTER SET utf8mb4;"
            async with temp_conn.cursor() as cursor:
                await cursor.execute(create_db_sql)
            await temp_conn.commit()
            temp_conn.close()
            print(f"[OK] MySQL数据库 '{db_name}' 已创建/存在")

            # 3. 创建连接池
            mysql_config_full = {
                "host": config.MYSQL_CONFIG.get("host"),
                "port": config.MYSQL_CONFIG.get("port", 3306),
                "user": config.MYSQL_CONFIG.get("user"),
                "password": config.MYSQL_CONFIG.get("password"),
                "db": config.MYSQL_CONFIG.get("database"),  # aiomysql 使用 'db' 而不是 'database'
                "charset": config.MYSQL_CONFIG.get("charset", "utf8mb4"),
                "connect_timeout": 10,
                "minsize": 1,
                "maxsize": 10
            }
            mysql_pool = await aiomysql.create_pool(**mysql_config_full)

            # 创建表的SQL
            create_table_sqls = [
                """
                CREATE TABLE IF NOT EXISTS detect_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) COMMENT '上传文件名',
                    detections TEXT COMMENT '检测结果JSON字符串',
                    ai_analysis TEXT COMMENT '豆包AI分析结果',
                    question TEXT COMMENT '用户提问文本',
                    create_time DATETIME NOT NULL COMMENT '检测时间',
                    file_path VARCHAR(255) COMMENT '文件存储路径'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='YOLO检测日志表'
                """,
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id VARCHAR(50) PRIMARY KEY,
                    session_id VARCHAR(50) NOT NULL,
                    role ENUM('user', 'assistant') NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    intent VARCHAR(50),
                    sentiment VARCHAR(20),
                    metadata JSON,
                    INDEX idx_session_time (session_id, timestamp),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表'
                """,
                """
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    session_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL,
                    state ENUM('new', 'active', 'paused', 'completed', 'error') DEFAULT 'new',
                    created_at DATETIME NOT NULL,
                    ended_at DATETIME NULL,
                    message_count INT DEFAULT 0,
                    INDEX idx_user_created (user_id, created_at),
                    INDEX idx_state (state)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话会话表'
                """,
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id VARCHAR(50) PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    priority INT DEFAULT 2,
                    status ENUM('pending', 'running', 'completed', 'failed', 'cancelled') DEFAULT 'pending',
                    progress FLOAT DEFAULT 0.0,
                    current_step INT DEFAULT 0,
                    result JSON,
                    error_message TEXT,
                    created_at DATETIME NOT NULL,
                    created_by VARCHAR(100) NOT NULL,
                    started_at DATETIME NULL,
                    completed_at DATETIME NULL,
                    estimated_time INT COMMENT '预估执行时间(秒)',
                    INDEX idx_status_created (status, created_at),
                    INDEX idx_created_by (created_by)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务表'
                """,
                """
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id VARCHAR(50) PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    doc_type VARCHAR(50) DEFAULT 'custom',
                    source VARCHAR(200),
                    tags JSON,
                    embedding_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    created_by VARCHAR(100),
                    INDEX idx_type_created (doc_type, created_at),
                    INDEX idx_source (source),
                    FULLTEXT idx_content (content, title)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识文档表'
                """,
                """
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    metric_type VARCHAR(50) NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    labels JSON,
                    timestamp DATETIME NOT NULL,
                    INDEX idx_type_name_time (metric_type, metric_name, timestamp),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统监控指标表'
                """
            ]

            # 执行每个表的创建语句
            async with mysql_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    for sql in create_table_sqls:
                        await cursor.execute(sql)

                # 自动修复字段约束
                await self._fix_mysql_constraints(conn, db_name)
                await conn.commit()

            print("[OK] MySQL检测日志表初始化完成")
            return mysql_pool

        except aiomysql.OperationalError as e:
            print(f"[FAIL] MySQL连接失败：{str(e)}")
            return None
        except Exception as e:
            print(f"[WARN] MySQL初始化失败：{str(e)}")
            return None

    async def _fix_mysql_constraints(self, mysql_conn, db_name):
        """异步修复MySQL字段约束"""
        try:
            async with mysql_conn.cursor() as cursor:
                # 修复question字段
                check_column_sql = f"""
                SELECT COLUMN_NAME
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = '{db_name}'
                AND TABLE_NAME = 'detect_log'
                AND COLUMN_NAME = 'question';
                """
                await cursor.execute(check_column_sql)
                column_exists = await cursor.fetchone()

                if not column_exists:
                    add_column_sql = """
                    ALTER TABLE detect_log
                    ADD COLUMN question TEXT COMMENT '用户提问文本'
                    AFTER ai_analysis;
                    """
                    await cursor.execute(add_column_sql)
                    print("[OK] 自动补全缺失的question字段")

                # 修复filename字段的非空约束
                check_null_sql = f"""
                SELECT IS_NULLABLE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = '{db_name}'
                AND TABLE_NAME = 'detect_log'
                AND COLUMN_NAME = 'filename';
                """
                await cursor.execute(check_null_sql)
                result = await cursor.fetchone()
                is_nullable = result[0] if result else 'YES'

                if is_nullable == 'NO':
                    alter_filename_sql = """
                    ALTER TABLE detect_log
                    MODIFY COLUMN filename VARCHAR(255) COMMENT '上传文件名';
                    """
                    await cursor.execute(alter_filename_sql)
                    print("[OK] 自动修复filename字段：去掉非空约束")

                # 修复detections字段允许为空
                check_detections_null = f"""
                SELECT IS_NULLABLE
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = '{db_name}'
                AND TABLE_NAME = 'detect_log'
                AND COLUMN_NAME = 'detections';
                """
                await cursor.execute(check_detections_null)
                result = await cursor.fetchone()
                detections_nullable = result[0] if result else 'YES'

                if detections_nullable == 'NO':
                    alter_detections_sql = """
                    ALTER TABLE detect_log
                    MODIFY COLUMN detections TEXT COMMENT '检测结果JSON字符串';
                    """
                    await cursor.execute(alter_detections_sql)
                    print("[OK] 自动修复detections字段：去掉非空约束")

        except Exception as e:
            print(f"[WARN] 自动修复约束失败：{str(e)}")

    async def _init_redis(self) -> Optional[aioredis.Redis]:
        """
        异步初始化Redis客户端

        Returns:
            Redis客户端对象或None
        """
        try:
            # 校验Redis基础配置
            if not config.REDIS_CONFIG.get("host"):
                print("[WARN] Redis配置不完整，跳过Redis初始化")
                return None

            # 构建Redis连接参数
            redis_params = {
                "host": config.REDIS_CONFIG['host'],
                "port": config.REDIS_CONFIG.get('port', 6379),
                "db": config.REDIS_CONFIG.get('db', 0),
                "decode_responses": True,
                "encoding": 'utf-8'
            }
            
            # 如果有密码，添加密码参数
            if config.REDIS_CONFIG.get('password'):
                redis_params['password'] = config.REDIS_CONFIG['password']
            
            # 建立连接并测试
            redis_client = aioredis.Redis(**redis_params)
            await redis_client.ping()  # 测试连接
            print("[OK] Redis初始化成功")
            return redis_client

        except Exception as e:
            print(f"[WARN] Redis初始化失败：{str(e)}")
            return None

    async def save_interaction(self, filename: str, question: str, detections: List[Dict],
                        ai_analysis: str, file_path: str = None):
        """异步保存交互记录到数据库"""
        # 保存到MySQL
        await self._save_to_mysql(filename, question, detections, ai_analysis, file_path)

        # 保存到Redis
        await self._save_to_redis(filename, question, detections, ai_analysis)

    async def _save_to_mysql(self, filename, question, detections, ai_analysis, file_path):
        """异步保存交互结果到MySQL"""
        if not self.mysql_pool:
            return False

        try:
            insert_sql = """
            INSERT INTO detect_log (filename, question, detections, ai_analysis, create_time, file_path)
            VALUES (%s, %s, %s, %s, %s, %s);
            """

            # 空值处理
            filename_str = filename if filename else ""
            detections_str = str(detections) if detections else ""
            question_str = question if question else ""
            ai_analysis_str = ai_analysis if ai_analysis else ""
            file_path_str = file_path if file_path else ""

            async with self.mysql_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(insert_sql, (
                        filename_str, question_str, detections_str, ai_analysis_str,
                        datetime.now(), file_path_str
                    ))
                await conn.commit()
            
            print(f"[OK] 交互记录已保存到MySQL")
            return True

        except Exception as e:
            print(f"[WARN] 保存MySQL失败：{str(e)}")
            return False

    async def _save_to_redis(self, filename, question, detections, ai_analysis, expire=3600):
        """异步缓存交互结果到Redis"""
        if not self.redis_client:
            return False

        try:
            # 构造唯一缓存Key
            cache_key = f"yolo:interact:{int(time.time())}:{filename if filename else 'text'}"

            # 构造缓存值
            cache_value = {
                "question": question or "",
                "detections": str(detections) if detections else "",
                "ai_analysis": ai_analysis,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "filename": filename or ""
            }

            # 保存到Redis
            await self.redis_client.hset(cache_key, mapping=cache_value)
            await self.redis_client.expire(cache_key, expire)
            print(f"[OK] 交互记录已缓存到Redis：{cache_key}（过期时间{expire}秒）")
            return True

        except Exception as e:
            print(f"[WARN] 保存Redis失败：{str(e)}")
            return False

    async def get_interaction_history(self, limit: int = 100) -> List[Dict]:
        """
        异步获取交互历史记录

        Args:
            limit: 记录数量限制

        Returns:
            历史记录列表
        """
        if not self.mysql_pool:
            return []

        try:
            query_sql = """
            SELECT filename, question, detections, ai_analysis, create_time, file_path
            FROM detect_log
            ORDER BY create_time DESC
            LIMIT %s;
            """

            async with self.mysql_pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query_sql, (limit,))
                    results = await cursor.fetchall()

            # 格式化结果
            history_list = []
            for row in results:
                detections_data = eval(row[2]) if row[2] and row[2] != "" else None
                history_list.append({
                    "文件名": row[0] if row[0] else "纯文字提问",
                    "用户提问": row[1] if row[1] else "",
                    "检测结果": detections_data,
                    "智能分析": row[3] if row[3] else "",
                    "交互时间": row[4].strftime("%Y-%m-%d %H:%M:%S"),
                    "文件路径": row[5] if row[5] else ""
                })

            return history_list

        except Exception as e:
            print(f"[FAIL] 历史查询异常：{str(e)}")
            return []

    async def close(self):
        """关闭数据库连接"""
        if self.mysql_pool:
            self.mysql_pool.close()
            await self.mysql_pool.wait_closed()
        
        if self.redis_client:
            await self.redis_client.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.init_databases()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()