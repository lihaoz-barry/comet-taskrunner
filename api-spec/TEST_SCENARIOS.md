# Test Scenarios & Use Cases

## 🎯 E-commerce Testing Scenarios

### Scenario 1: 1688 Product Analysis (`/1mu3`)

**背景 (Background)**
- 1688.com 是阿里巴巴的批发平台
- 需要提取产品信息、价格、供应商数据

**测试步骤 (Test Steps)**
1. 启动后端服务器
2. 在 Postman 中打开 **"AI Task - /1mu3 Prompt"**
3. 点击 **Send**
4. 观察 Comet 浏览器自动化过程:
   - ✅ 浏览器启动
   - ✅ AI Assistant 按钮被点击
   - ✅ `/1mu3` 命令被输入
   - ✅ Enter 键被按下两次 (slash command)
5. 使用 **"Poll Task Until Complete"** 监控状态

**预期结果 (Expected Results)**
- Status: `started` → `running` → `done`
- AI 会在浏览器中执行 1mu3 相关的自动化任务
- Task ID 被保存到环境变量

**实际应用 (Real-world Application)**
- 批量提取 1688 产品数据
- 价格监控
- 供应商信息收集

---

### Scenario 2: IKEA Product Query (`/ikea`)

**背景 (Background)**
- IKEA 产品目录分析
- 家具产品信息提取

**测试步骤 (Test Steps)**
1. 在 Postman 中打开 **"AI Task - /ikea Prompt"**
2. 点击 **Send**
3. 查看浏览器自动化
4. 监控任务状态

**预期结果 (Expected Results)**
- AI 处理 IKEA 相关查询
- 自动化序列成功完成
- 7/7 步骤全部成功

**实际应用 (Real-world Application)**
- IKEA 产品目录爬取
- 价格比较
- 库存监控

---

### Scenario 3: Amazon Product Search (`/amazon`)

**背景 (Background)**
- Amazon 产品搜索和数据提取
- 电商竞品分析

**测试步骤 (Test Steps)**
1. 打开 **"AI Task - /amazon Prompt"**
2. 发送请求
3. 观察自动化执行

**预期结果 (Expected Results)**
- Amazon 搜索任务被执行
- 数据提取成功

**实际应用 (Real-world Application)**
- 价格追踪
- 竞品分析
- 产品评论收集

---

## 🤖 General AI Browser Automation

### Scenario 4: Web Page Summarization

**任务描述 (Task Description)**
```json
{
  "instruction": "Please summarize the main content of this webpage in 3-5 bullet points."
}
```

**使用场景 (Use Cases)**
- 快速理解网页内容
- 新闻摘要
- 文档总结
- 研究资料整理

**测试流程 (Test Flow)**
1. 先用 **URL Task** 导航到目标网页
2. 然后发送 **Web Summarization** AI 任务
3. AI 会分析当前页面并生成摘要

**技术要点 (Technical Notes)**
- 适合文本密集型页面
- AI 需要理解页面结构
- 输出格式为 bullet points

---

### Scenario 5: Product Data Extraction

**任务描述 (Task Description)**
```json
{
  "instruction": "Extract all product prices from this page and list them in a table format."
}
```

**使用场景 (Use Cases)**
- 价格监控
- 批量数据收集
- 市场分析
- 竞品价格比较

**测试流程 (Test Flow)**
1. 导航到产品列表页面 (如 Amazon search results)
2. 发送数据提取任务
3. AI 识别价格元素
4. 以表格形式输出

**预期输出格式 (Expected Output Format)**
```
| Product | Price |
|---------|-------|
| Item 1  | $9.99 |
| Item 2  | $14.99|
```

---

### Scenario 6: Image Analysis

**任务描述 (Task Description)**
```json
{
  "instruction": "Analyze the images on this page and describe what products are shown."
}
```

**使用场景 (Use Cases)**
- 产品图片分类
- 视觉内容分析
- 图片质量评估
- 产品识别

**测试流程 (Test Flow)**
1. 导航到包含产品图片的页面
2. 发送图片分析任务
3. AI 使用多模态能力分析图片
4. 生成产品描述

**技术要点 (Technical Notes)**
- 需要 AI 的视觉理解能力
- 适合图片密集型电商网站
- 可以识别产品类型、颜色、特征

---

### Scenario 7: Translation

**任务描述 (Task Description)**
```json
{
  "instruction": "Translate the main heading of this page to English."
}
```

**使用场景 (Use Cases)**
- 跨境电商 (1688, Taobao → English)
- 多语言内容处理
- 国际市场研究

**测试流程 (Test Flow)**
1. 导航到中文页面 (如 1688.com)
2. 发送翻译任务
3. AI 提取主标题并翻译

**实际应用 (Real-world Application)**
- 1688 供应商页面翻译
- 产品标题本地化
- 多语言支持

---

### Scenario 8: Comparative Analysis

**任务描述 (Task Description)**
```json
{
  "instruction": "Compare the features of the top 3 products on this page and create a comparison table."
}
```

**使用场景 (Use Cases)**
- 产品对比
- 功能分析
- 购买决策支持
- 竞品研究

**测试流程 (Test Flow)**
1. 导航到产品搜索结果页
2. 发送对比分析任务
3. AI 提取前3个产品的特征
4. 生成对比表格

**预期输出格式 (Expected Output Format)**
```
| Feature    | Product 1 | Product 2 | Product 3 |
|------------|-----------|-----------|-----------|
| Price      | $50       | $60       | $55       |
| Rating     | 4.5⭐     | 4.2⭐     | 4.7⭐     |
| Material   | Cotton    | Polyester | Blend     |
```

---

## 🔄 Workflow Testing Scenarios

### Complete E-commerce Research Workflow

**目标 (Objective)**
从 1688 找到产品 → 分析 → 翻译 → 提取数据

**完整步骤 (Complete Steps)**

1. **Step 1: Navigate to 1688**
   ```
   Request: Execute URL Task - 1688.com
   ```

2. **Step 2: Analyze with /1mu3**
   ```
   Request: AI Task - /1mu3 Prompt
   ```

3. **Step 3: Extract Product Data**
   ```
   Request: AI Task - Data Extraction
   Body: "Extract all product prices and supplier names"
   ```

4. **Step 4: Translate to English**
   ```
   Request: AI Task - Translation Request
   Body: "Translate all product names to English"
   ```

5. **Step 5: Create Comparison**
   ```
   Request: AI Task - Comparative Analysis
   Body: "Compare top 3 products by price and features"
   ```

**监控整个流程 (Monitor Entire Flow)**
- 使用 **Get Queue Status** 查看所有任务
- 每个任务用 **Poll Task Until Complete** 监控
- 记录每个步骤的 task_id

---

## 📊 Performance Testing Scenarios

### Concurrent Task Submission

**测试目标 (Test Objective)**
验证任务队列处理能力

**测试步骤 (Test Steps)**
1. 快速连续提交 5 个 AI 任务
2. 观察队列行为:
   - 第一个任务: `status: "started"`
   - 其他任务: `status: "queued"`
3. 使用 **Get Queue Status** 查看队列长度
4. 等待所有任务完成

**预期结果 (Expected Results)**
- 任务按顺序执行 (sequential processing)
- 队列正确管理
- 无任务丢失
- 状态正确转换

---

### Long-running Task Monitoring

**测试目标 (Test Objective)**
测试长时间运行任务的监控

**测试步骤 (Test Steps)**
1. 提交复杂的 AI 任务 (如对比分析)
2. 使用 **Poll Task Until Complete** 持续监控
3. 观察自动化进度:
   ```json
   {
     "automation_progress": {
       "total_steps": 7,
       "completed_steps": 5,
       "current_step": 6,
       "progress_percent": 71
     }
   }
   ```

**预期结果 (Expected Results)**
- 进度信息实时更新
- 轮询脚本正确工作
- 最终状态为 `done` 或 `failed`

---

## 🧪 Error Handling Scenarios

### Scenario: Invalid Instruction

**测试 (Test)**
```json
POST /execute/ai
{
  "instruction": ""
}
```

**预期结果 (Expected Result)**
- Status Code: `400 Bad Request`
- Error: `"instruction is required"`

---

### Scenario: Task Not Found

**测试 (Test)**
```
GET /status/invalid-task-id-12345
```

**预期结果 (Expected Result)**
- Status Code: `404 Not Found`
- Error: `"Task ID not found"`

---

### Scenario: Server Offline

**测试 (Test)**
关闭后端服务器,然后发送请求

**预期结果 (Expected Result)**
- Postman 显示 connection error
- 提示检查服务器状态

---

## 📝 Manual Testing Checklist

### Pre-deployment Checklist

- [ ] Health Check 返回 200
- [ ] URL Task 成功启动浏览器
- [ ] AI Task `/1mu3` 成功执行
- [ ] AI Task `/ikea` 成功执行
- [ ] Task status 正确更新
- [ ] Queue status 显示正确
- [ ] 自动化步骤全部完成 (7/7)
- [ ] 错误处理正确 (400, 404)
- [ ] 并发任务正确排队
- [ ] 轮询脚本工作正常

### Regression Testing (回归测试)

每次更新后运行:
1. **Collection Runner** 运行所有测试
2. 检查所有测试通过
3. 验证没有新的错误
4. 性能没有退化

---

## 🎬 Demo Scenarios (演示场景)

### Demo 1: Quick Start Demo

**时长 (Duration)**: 2 分钟

1. 健康检查 (5秒)
2. 提交 `/1mu3` 任务 (10秒)
3. 观察浏览器自动化 (60秒)
4. 检查任务状态 (5秒)
5. 展示队列状态 (10秒)

### Demo 2: Complete Workflow Demo

**时长 (Duration)**: 5-10 分钟

1. 导航到 1688
2. AI 分析产品
3. 提取数据
4. 翻译内容
5. 生成报告

---

## 💡 Tips & Best Practices

### Testing Tips

1. **Always start with Health Check**
   确保服务器在线

2. **Use environment variables**
   不要硬编码 task_id

3. **Monitor queue status**
   了解系统负载

4. **Enable Console**
   查看详细日志

5. **Save responses as examples**
   文档化成功和失败响应

### Debugging Tips

1. **Check automation progress**
   ```json
   {
     "automation_progress": {
       "step_details": [...]
     }
   }
   ```

2. **Review logs**
   后端日志显示详细的自动化步骤

3. **Screenshot analysis**
   检查 `screenshots/` 目录

4. **Template matching**
   确保模板图片正确

---

**Last Updated**: December 2025  
**Version**: 1.0
