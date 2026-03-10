# 🌾 YOLO11 智能农业系统

> 基于 FastAPI 的现代化智能农业应用，集成 AI 检测、农业资讯和用户管理

## ✨ 核心功能

- 🤖 **AI 智能助手**：YOLO11 目标检测 + RAG 知识问答
- 📰 **农业资讯**：新闻浏览、搜索、分类、收藏
- 👤 **用户系统**：注册登录、个人中心、历史记录

## 🎯 技术亮点

- ⚡ FastAPI 异步框架，高性能并发
- 🔒 JWT 认证 + bcrypt 加密
- 📱 响应式设计，多端适配
- 🐳 Docker Compose 一键部署

## 🚀 快速开始

### 方式一：本地运行

```bash
# 1. 安装依赖
pip install -r requirements_fastapi.txt

# 2. 配置环境变量
copy .env.example .env

# 3. 初始化数据库
python init_database.py

# 4. 启动应用
python main.py
```

### 方式二：Docker 部署

```bash
docker-compose -f docker-compose.development.yml up -d
```

### 访问应用

- 主页：http://localhost:8000
- API 文档：http://localhost:8000/docs

## 📚 文档

**[📖 文档导航](📖文档导航.md)** - 快速找到你需要的文档

### 快速开始
- **[🚀 快速上手](快速上手.md)** - 5 分钟快速启动（新手必读）
- [启动指南](启动指南.md) - 详细的启动步骤

### 使用指南
- **[📖 应用手册](应用手册.md)** - 完整的使用指南（推荐阅读）
- [使用说明](使用说明.md) - 功能使用说明
- [快速参考](快速参考.md) - 常用命令速查

### 项目信息
- [项目文件清单](项目文件清单.md) - 完整的文件说明
- [清理完成总结](清理完成总结.md) - 项目优化报告

## 📁 项目结构

```
yolo11_fastapi/
├── config/          # 配置模块
├── models/          # 数据模型
├── schemas/         # 数据验证
├── crud/            # 数据访问层
├── routers/         # API 路由
├── services/        # 业务逻辑层
├── templates/       # HTML 模板
├── static/          # 静态资源
└── main.py          # 应用入口
```

## 🔧 技术栈

**后端**：FastAPI + MySQL + Redis + SQLAlchemy  
**AI**：YOLO11 + LangChain + FAISS  
**认证**：JWT + bcrypt

## 📄 许可证

MIT License
