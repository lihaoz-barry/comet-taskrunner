# Azure Windows Server 部署指南 (Expose Port)

本指南将指导您将 Comet Task Runner 后端部署到 Azure Windows Server，并将其端口暴露给公网访问。

---

## ⚠️ 安全警告 (必读)

**风险**: 将此服务直接暴露在公网 (`0.0.0.0`) 意味着**任何人**只要知道您的 IP 和端口，就可以：
1. 打开您服务器上的浏览器访问任意网站
2. 控制您服务器的鼠标和键盘 (通过 AI 任务)
3. 潜在地执行恶意操作

**建议**: 
- **最低限度**: 使用简单的 API Key 验证 (本指南包含)
- **推荐**: 使用 VPN 或 IP 白名单限制访问
- **生产环境**: 使用 Nginx 反向代理 + HTTPS + 身份验证

---

## 🚀 步骤 1: 修改代码 (允许外部连接)

默认情况下，Flask 只监听 `127.0.0.1` (仅本机)。需要修改为 `0.0.0.0`。

### 修改 `src/backend.py`

找到文件末尾的 `app.run` 部分：

```python
# 修改前
app.run(host='127.0.0.1', port=5000, debug=False)

# 修改后
app.run(host='0.0.0.0', port=5000, debug=False)
```

**可选：添加简单的 API Key 验证**

在 `src/backend.py` 顶部添加：

```python
from functools import wraps

API_KEY = "my-secret-password-123"  # 设置您的密码

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function
```

然后将装饰器应用到路由上：

```python
@app.route('/execute/ai', methods=['POST'])
@require_api_key  # <--- 添加这一行
def execute_ai():
    # ...
```

---

## ☁️ 步骤 2: Azure 门户配置 (NSG)

您需要在 Azure 的网络层放行 5000 端口。

1. 登录 **Azure Portal** (portal.azure.com)
2. 找到您的 **Virtual Machine (VM)**
3. 在左侧菜单点击 **Networking (网络)**
4. 点击 **Add inbound port rule (添加入站端口规则)**
5. 配置规则：
   - **Source**: `Any` (或限制为您自己的 IP)
   - **Source port ranges**: `*`
   - **Destination**: `Any`
   - **Destination port ranges**: `5000` (或您使用的端口)
   - **Protocol**: `TCP`
   - **Action**: `Allow`
   - **Priority**: `310` (或其他低数字)
   - **Name**: `Allow_Comet_Backend`
6. 点击 **Add**

---

## 🖥️ 步骤 3: Windows Server 内部防火墙

即使 Azure 放行了，Windows 自身的防火墙也可能拦截。

1. 远程桌面 (RDP) 连接到您的 Azure VM
2. 打开 **PowerShell (管理员)**
3. 运行以下命令放行 5000 端口：

```powershell
New-NetFirewallRule -DisplayName "Comet Backend" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

或者通过 GUI：
1. 搜索 "Windows Defender Firewall with Advanced Security"
2. 点击 **Inbound Rules** -> **New Rule...**
3. 选择 **Port** -> **TCP**, **Specific local ports**: `5000`
4. 选择 **Allow the connection**
5. 勾选 Domain, Private, Public
6. Name: `Comet Backend`

---

## 🧪 步骤 4: 验证连接

### 在本地电脑 (您的开发机)

使用 Postman 或 curl 测试连接：

```bash
# 替换为您的 Azure VM 公网 IP
curl http://<AZURE_VM_IP>:5000/health
```

如果配置了 API Key：
```bash
curl -H "X-API-Key: my-secret-password-123" http://<AZURE_VM_IP>:5000/health
```

---

## ❓ 常见问题

### Q: 为什么修改了 0.0.0.0 还是连不上？
**A**: 检查顺序：
1. **本地测试**: 在 VM 内部用浏览器访问 `http://localhost:5000` 能通吗？
2. **防火墙**: 暂时关闭 Windows 防火墙测试 (`Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False`)，如果通了说明是防火墙规则问题。
3. **Azure NSG**: 确认规则已生效（有时有延迟）。
4. **公网 IP**: 确认您使用的是 VM 的 Public IP，且该 IP 是静态的或未改变。

### Q: 可以不加 Token 吗？
**A**: **技术上可以**。如果您只是临时测试，或者在一个受信任的内网环境中，可以不加。但如果是公网，**强烈建议**至少加一个简单的 Token，或者在 Azure NSG 中将 `Source` 限制为您自己的 IP 地址，这样只有您能访问。

### Q: 如何让它在后台一直运行？
**A**: 
1. 使用 `start_background.bat` (使用 pythonw)
2. 或者使用 **NSSM** (Non-Sucking Service Manager) 将其注册为 Windows 服务：
   ```batch
   nssm install CometBackend "C:\Python311\python.exe" "C:\path\to\src\backend.py"
   nssm start CometBackend
   ```

---

**总结**:
1. 代码改 `0.0.0.0`
2. Azure NSG 放行 5000
3. Windows 防火墙放行 5000
4. (推荐) 加个 API Key

祝部署顺利！🚀
