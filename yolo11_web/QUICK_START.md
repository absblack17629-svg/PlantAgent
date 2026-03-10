# 快速测试指南

## 1. 启动服务

打开**两个**命令提示符窗口：

**窗口1 - 启动后端：**
```bash
cd C:/Users/1/Desktop/file/Fastapi_backend/yolo11_web
python main.py
```

**窗口2 - 启动前端：**
```bash
cd C:/Users/1/Desktop/file/Fastapi_backend/yolo11_web/frontend
npm run dev
```

## 2. 访问系统

浏览器访问：http://localhost:3000

点击左侧【智能助手】菜单

## 3. 测试项目

### 测试1：简单对话
输入：`你好`
预期：返回问候语

### 测试2：知识查询
输入：`什么是稻瘟病？`
预期：返回病害详细信息

### 测试3：图片检测（重要！）
1. 从 `C:\yolov8\ultralytics-8.0.224\yolov8_dataset\train\images` 复制一张图片到桌面
2. 在智能助手中上传图片
3. 输入：`帮我检测这张图片的病害`

**预期结果**：显示"🔬 检测到 X 个对象..."（而不是"🔬 mock"）

## 4. 查看调试日志

测试时请观察**后端窗口**的输出，应看到：
```
[9-Node] Input: 你好... image_path=None
[9-Node] skill_client available: True
[ToolAgent] Executing DetectionSkill.detect_objects with image_path=...
[9-Node] Final response: 你好！我是水稻病害智能助手🌾 ...
```

## 5. 问题排查

**如果图片检测仍返回"mock"：**
- 检查后端日志中 `PlanningSkillAgent` 是否接收到 `skill_client`
- 确认日志中出现 `[9-Node] skill_client available: True`

**如果知识查询返回"抱歉"：**
- 检查后端日志是否有 RAG 服务初始化错误
- 首次查询可能需要更长时间初始化

**如果服务无法启动：**
- 检查端口 8000 和 3000 是否被占用
- 使用 `netstat -ano | findstr :8000` 查看占用进程

---

## 快速命令参考

```bash
# 检查服务状态
curl http://localhost:8000/info

# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# 查看进程
 tasklist | findstr python
 tasklist | findstr node
```

---

**祝测试顺利！如有问题请提供具体的错误日志。**
