# YOLO11 智能体对话界面

基于 LangChain Agent Chat UI 的现代化对话界面。

## 快速开始

### 1. 安装依赖
```bash
pnpm install
```

### 2. 配置环境变量
复制 `.env.example` 到 `.env` 并配置：
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ASSISTANT_ID=agent
```

### 3. 启动开发服务器
```bash
pnpm dev
```

访问 http://localhost:3000

## 功能特性

- ✅ 流式对话输出
- ✅ Markdown 渲染
- ✅ 代码语法高亮
- ✅ 深色/浅色主题
- ✅ 响应式设计
- ✅ 多线程管理

## 技术栈

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- LangChain SDK

## 开发命令

```bash
# 开发模式
pnpm dev

# 构建生产版本
pnpm build

# 启动生产服务
pnpm start

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

## 项目结构

```
frontend/
├── src/
│   ├── app/          # Next.js 应用路由
│   ├── components/   # React 组件
│   ├── providers/    # Context 提供者
│   └── utils/        # 工具函数
├── public/           # 静态资源
└── package.json      # 依赖配置
```

## 连接后端

确保后端服务运行在 http://localhost:8000

后端需要实现以下 API 端点：
- `POST /threads` - 创建对话线程
- `POST /threads/{id}/runs/stream` - 流式对话
- `GET /threads/{id}/state` - 获取线程状态

## 更多信息

查看 [LangChain Agent Chat UI 文档](https://github.com/langchain-ai/agent-chat-ui)
