# 🚀 Postman 快速上手指南 (Quick Start Guide)

## 📥 导入步骤 (Import Steps)

### 1️⃣ 打开 Postman
- 下载并安装 [Postman](https://www.postman.com/downloads/)
- 或使用 Web 版本

### 2️⃣ 导入 Collection
1. 点击左上角 **Import** 按钮
2. 选择文件: `Comet_TaskRunner_Collection.postman_collection.json`
3. 点击 **Import** 完成导入

### 3️⃣ 导入 Environment
1. 再次点击 **Import** 按钮
2. 选择文件: `Comet_TaskRunner_Local.postman_environment.json`
3. 点击 **Import** 完成导入

### 4️⃣ 选择环境
- 在右上角的环境下拉菜单中选择 **"Comet TaskRunner - Local"**

## ✅ 测试流程 (Testing Workflow)

### 基础测试 (Basic Tests)

**步骤 1: 健康检查**
```
请求: Health Check
方法: GET /health
目的: 确认服务器运行正常
```

**步骤 2: 提交 AI 任务**
```
请求: AI Task - /1mu3 Prompt
方法: POST /execute/ai
Body: { "instruction": "/1mu3" }
目的: 创建 1688 产品分析任务
自动操作: task_id 会自动保存到环境变量
```

**步骤 3: 检查任务状态**
```
请求: Get Task Status
方法: GET /status/{{task_id}}
目的: 查看任务执行状态
自动操作: 使用步骤 2 保存的 task_id
```

**步骤 4: 查看队列状态**
```
请求: Get Queue Status
方法: GET /manager/status
目的: 查看所有任务的队列状态
```

### 🎯 重点测试场景 (Key Test Scenarios)

#### 1. E-commerce 电商测试

**测试 1: 1688.com 分析**
```json
POST /execute/ai
{
  "instruction": "/1mu3"
}
```
- 用途: 测试 1688 产品页面分析功能
- 预期: AI 会在浏览器中打开并分析产品信息

**测试 2: IKEA 产品查询**
```json
POST /execute/ai
{
  "instruction": "/ikea"
}
```
- 用途: 测试 IKEA 产品信息提取
- 预期: AI 会处理 IKEA 相关的产品数据

**测试 3: Amazon 搜索**
```json
POST /execute/ai
{
  "instruction": "/amazon"
}
```
- 用途: 测试 Amazon 产品搜索
- 预期: AI 会执行 Amazon 产品搜索任务

#### 2. 通用 AI 任务测试

**网页摘要**
```json
POST /execute/ai
{
  "instruction": "Please summarize the main content of this webpage in 3-5 bullet points."
}
```

**数据提取**
```json
POST /execute/ai
{
  "instruction": "Extract all product prices from this page and list them in a table format."
}
```

**图片分析**
```json
POST /execute/ai
{
  "instruction": "Analyze the images on this page and describe what products are shown."
}
```

## 🔄 自动化测试 (Automated Testing)

### 使用 Collection Runner

1. 选择 Collection: **Comet Task Runner API**
2. 点击 **Run** 按钮
3. 选择要运行的请求
4. 点击 **Run Comet Task Runner API**
5. 查看测试结果统计

### 使用自动轮询 (Auto-Polling)

使用 **"Poll Task Until Complete"** 请求:
- 自动每 2 秒检查一次任务状态
- 直到任务完成或失败才停止
- 无需手动刷新

## 📊 测试脚本功能 (Test Script Features)

每个请求都包含自动化测试脚本:

### ✅ 自动验证
- 检查 HTTP 状态码 (200, 400, 404等)
- 验证 JSON 响应结构
- 确认必需字段存在

### 💾 自动保存
- 提取 `task_id` 并保存到环境变量
- 后续请求可自动使用该 ID
- 无需手动复制粘贴

### 📝 日志输出
- 在 Console 中显示详细信息
- 方便调试和追踪

## 🎨 Collection 结构 (Collection Structure)

```
Comet Task Runner API
├── 📁 Health & Status (健康检查与状态)
│   ├── Health Check
│   ├── Get Queue Status
│   └── Get All Jobs
├── 📁 URL Tasks (URL 任务)
│   ├── Execute URL Task - Google
│   └── Execute URL Task - 1688.com
├── 📁 AI Prompt Tasks - E-commerce (电商 AI 任务)
│   ├── AI Task - /1mu3 Prompt ⭐
│   ├── AI Task - /ikea Prompt ⭐
│   └── AI Task - /amazon Prompt
├── 📁 AI Prompt Tasks - General (通用 AI 任务)
│   ├── Web Summarization
│   ├── Data Extraction
│   ├── Image Analysis
│   ├── Translation Request
│   └── Comparative Analysis
├── 📁 Task Status Monitoring (状态监控)
│   ├── Get Task Status
│   └── Poll Task Until Complete
└── 📁 Manual Callbacks (手动回调)
    ├── Mark Task as Done
    └── Mark Task as Failed
```

⭐ = 您特别要求的测试用例

## 💡 高级功能 (Advanced Features)

### 1. 生成 API 文档

1. 选择 Collection
2. 点击右上角 **View Documentation**
3. 点击 **Publish** 创建公开文档
4. 分享 URL 给团队成员

### 2. Newman CLI (命令行测试)

安装 Newman:
```bash
npm install -g newman
```

运行测试:
```bash
cd api-spec
newman run Comet_TaskRunner_Collection.postman_collection.json \
  -e Comet_TaskRunner_Local.postman_environment.json
```

### 3. 监控 (Monitors)

设置自动化健康检查:
1. 点击 **Monitors** 标签
2. 创建新监控
3. 设置执行频率 (如每 5 分钟)
4. 配置邮件提醒

### 4. Mock Server

创建模拟服务器用于前端开发:
1. 右键点击 Collection → **Mock Collection**
2. 配置 Mock Server
3. 使用 Mock URL 进行前端测试

## 🔧 自定义测试 (Customization)

### 添加新的测试用例

**示例: 添加新的电商平台测试**

1. 右键点击 **"AI Prompt Tasks - E-commerce"** 文件夹
2. 选择 **Add Request**
3. 配置请求:
   ```
   Name: AI Task - /taobao Prompt
   Method: POST
   URL: {{base_url}}/execute/ai
   Body (raw JSON):
   {
     "instruction": "/taobao"
   }
   ```
4. 添加测试脚本 (Tests 标签):
   ```javascript
   pm.test("Status code is 200", function () {
       pm.response.to.have.status(200);
   });
   
   pm.test("Task ID is returned", function () {
       var jsonData = pm.response.json();
       pm.expect(jsonData).to.have.property('task_id');
       pm.environment.set("task_id", jsonData.task_id);
   });
   ```
5. 保存并测试

## 📌 注意事项 (Important Notes)

### 前置条件
- ✅ 后端服务器必须运行在 `http://127.0.0.1:5000`
- ✅ Comet 浏览器已安装
- ✅ Python 环境配置完成

### 测试顺序
1. 先运行 **Health Check** 确认服务器在线
2. 再运行具体的任务测试
3. 使用 **Get Queue Status** 监控整体状态

### 环境变量
- `task_id` 会自动更新为最新创建的任务
- 如需测试特定任务,手动修改环境变量中的 `task_id`

## 🐛 故障排除 (Troubleshooting)

| 问题 | 解决方案 |
|------|----------|
| Connection refused | 确认后端服务器正在运行 |
| Task ID not found | 检查 task_id 环境变量是否正确 |
| Tests failing | 查看 Console 标签的详细错误信息 |
| Automation not working | 检查 Comet 浏览器是否正确安装 |

### 启用调试模式

1. 打开 Postman Console: <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>C</kbd> (Windows/Linux) 或 <kbd>Cmd</kbd>+<kbd>Option</kbd>+<kbd>C</kbd> (Mac)
2. 发送请求查看详细日志
3. 检查 Response 标签的 JSON 结构

## 📚 相关资源 (Resources)

- [项目 README](../README.md)
- [Backend API 文档](../src/backend.py)
- [Postman 官方文档](https://learning.postman.com/)
- [Newman CLI 指南](https://learning.postman.com/docs/running-collections/using-newman-cli/)

---

**创建日期**: 2025年12月
**版本**: 1.0
**语言**: 中文 / English
