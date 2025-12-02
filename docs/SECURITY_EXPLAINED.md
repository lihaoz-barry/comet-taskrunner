# 后端安全与网络配置详解

## 1. 为什么必须从 127.0.0.1 改成 0.0.0.0？

### 原理通俗解释
服务器可能有多个"耳朵"（网卡接口）：
- **Loopback 接口 (127.0.0.1)**: 这是一个虚拟接口，只能听到**本机内部**发出的声音。
- **Ethernet/Wi-Fi 接口 (例如 192.168.x.x 或 10.x.x.x)**: 连接到路由器或公网的接口。

### 区别
- **`host='127.0.0.1'`**: 程序告诉操作系统："我只监听 Loopback 接口"。
  - **后果**: 外部请求（从 Azure 负载均衡器或公网 IP 来的）会到达服务器的物理网卡，但 Flask 程序**并没有在监听那个网卡**，所以请求会被操作系统直接拒绝 (Connection Refused)。
  
- **`host='0.0.0.0'`**: 程序告诉操作系统："监听**所有**可用的网络接口"。
  - **后果**: 无论是本机请求，还是从公网网卡进来的请求，Flask 都能接收到。

---

## 2. API Key 与 GitHub 安全

### GitHub 的检测机制
GitHub 确实有 **Secret Scanning** 功能。
- 如果您写 `API_KEY = "sk-live-12345..."` (像 Stripe/OpenAI 格式)，GitHub 会**立刻阻止 push** 或发送警告。
- 如果您写 `API_KEY = "barry-secret-123"`，GitHub 可能不会拦截，但这依然是**Bad Practice**（不良实践）。因为任何能看到代码的人（包括未来的协作者）都能看到密码。

### 解决方案：环境变量 (.env)
不要把密码写在代码里，而是放在环境里。

**步骤 1: 安装 python-dotenv**
```bash
pip install python-dotenv
```

**步骤 2: 创建 `.env` 文件 (并加入 .gitignore)**
在项目根目录创建 `.env` 文件：
```ini
COMET_API_KEY=MySuperSecretPassword2025
```
**重要**: 确保 `.gitignore` 文件中包含 `.env`，这样它永远不会被上传到 GitHub。

**步骤 3: 修改代码读取变量**
```python
import os
from dotenv import load_dotenv

load_dotenv() # 加载 .env 文件

API_KEY = os.getenv('COMET_API_KEY') # 从环境读取
```

---

## 3. 平衡便捷性与安全性 (Localhost 免密)

您不希望在本地测试时每次都输入 Token。我们可以编写一个**智能装饰器**。

### 智能验证逻辑
1. 请求来了。
2. 检查来源 IP (`request.remote_addr`)。
3. 如果是 `127.0.0.1` -> **直接放行** (本地开发模式)。
4. 如果是外部 IP -> **检查 API Key**。

### 代码实现示例

```python
from functools import wraps
from flask import request, jsonify
import os

def smart_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. 本地豁免 (Localhost Exemption)
        if request.remote_addr == '127.0.0.1':
            return f(*args, **kwargs)
            
        # 2. 获取配置的 Key
        server_key = os.getenv('COMET_API_KEY')
        
        # 如果服务器没设密码，且暴露在公网，这是危险的！
        # 这里我们可以选择默认拒绝，或者允许(不推荐)
        if not server_key:
            return jsonify({"error": "Server configuration error: No API Key set"}), 500

        # 3. 验证 Header 中的 Key
        client_key = request.headers.get('X-API-Key')
        
        if client_key and client_key == server_key:
            return f(*args, **kwargs)
            
        return jsonify({"error": "Unauthorized"}), 401
        
    return decorated
```

这样，您在本地运行 `python src/backend.py` 时，Postman 不需要 Header 也能跑。但在 Azure 上，必须带 Header。

---

## 4. 安全性 Brainstorming (更多强化手段)

除了 API Key，还有哪些手段可以增强安全性？

### 🛡️ 1. IP 白名单 (Azure NSG) - **最推荐**
**原理**: 在 Azure 的网络防火墙层，只允许**您自己的 IP 地址**访问 5000 端口。
- **优点**: 即使没有 API Key，黑客也连不上端口。这是最底层的物理隔离。
- **操作**: 在 Azure Portal -> Networking -> Inbound Rules -> Source IP 填入您的公网 IP。

### 🔒 2. HTTPS (SSL/TLS)
**原理**: 目前您的 API 是 HTTP。API Key 在网线上是**明文传输**的。如果有人在咖啡厅监听 Wi-Fi，他能看到您的 Key。
- **改进**: 使用 HTTPS。
- **实现**: 在 Azure 上，通常使用 Nginx 反向代理来配置 SSL 证书 (Let's Encrypt 免费证书)，然后转发给 Flask。

### ⏱️ 3. 速率限制 (Rate Limiting)
**原理**: 防止有人用脚本一秒钟尝试 1000 个密码 (暴力破解)。
- **实现**: 使用 `Flask-Limiter` 库。
```python
from flask_limiter import Limiter
limiter = Limiter(app)

@app.route('/execute/ai')
@limiter.limit("5 per minute") # 每分钟只允许 5 次 AI 请求
def execute_ai(): ...
```

### 🧹 4. 输入验证 (Input Validation)
**原理**: 防止 AI 注入或命令注入。
- **风险**: 如果用户发送指令 `"/cmd delete system32"`, AI 可能会照做。
- **改进**: 在后端对 `instruction` 进行关键词过滤，禁止包含敏感词（如 "delete", "format", "system" 等）。

---

## 总结建议

1.  **代码修改**: 使用 `host='0.0.0.0'`。
2.  **配置管理**: 使用 `.env` 文件存储 Key，并 gitignore 掉。
3.  **验证逻辑**: 使用"本地豁免"的智能装饰器。
4.  **Azure 防御**: 在 NSG 中设置 **Source IP 白名单** (这是最简单且最有效的安全措施)。
