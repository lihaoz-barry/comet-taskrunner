# 环境配置快速参考卡

## ⚡ 快速开始 (5 分钟配置)

### 1️⃣ 安装 Python
```bash
# 下载 Python 3.10 或 3.11
https://www.python.org/downloads/

# 勾选 "Add Python to PATH"
```

### 2️⃣ 克隆项目
```bash
git clone https://github.com/lihaoz-barry/comet-taskrunner.git
cd comet-taskrunner
```

### 3️⃣ 安装依赖
```bash
pip install -r requirements.txt
```

### 4️⃣ 安装 Comet Browser
```bash
# 从官网下载安装
https://www.perplexity.ai/hub/blog/comet-browser
```

### 5️⃣ 启动项目
```bash
# 双击 start.bat
# 或手动启动:
python src/backend.py    # 终端 1
python src/frontend.py   # 终端 2
```

---

## 📋 系统要求总览

| 项目 | 要求 |
|------|------|
| **操作系统** | Windows 10/11 (64-bit) |
| **Python 版本** | 3.9, 3.10, 或 3.11 |
| **RAM** | 最少 4GB (推荐 8GB+) |
| **磁盘空间** | 500MB+ |
| **必需软件** | Comet Browser, VC++ Redistributable |

---

## 📦 依赖包列表

```txt
flask                  # REST API 后端
requests              # HTTP 客户端
psutil                # 进程监控
opencv-python>=4.8.0  # 模板匹配
numpy>=1.24.0         # 数值计算
mss>=9.0.0            # 屏幕截图
pyautogui>=0.9.50     # 鼠标键盘控制
Pillow>=10.0.0        # 图像处理
pywin32>=305          # Windows API
```

**安装命令**:
```bash
pip install -r requirements.txt
```

---

## 🧪 验证安装

### 测试所有依赖
```python
python -c "import flask, requests, psutil, cv2, numpy, mss, pyautogui, PIL, win32gui; print('✅ All OK!')"
```

### 测试后端
```bash
# 终端 1: 启动后端
python src/backend.py

# 终端 2: 测试健康检查
curl http://127.0.0.1:5000/health
```

预期响应:
```json
{"status":"ok","message":"Comet Task Runner is running"}
```

### 测试前端
```bash
python src/frontend.py
# 应该看到 GUI 窗口
```

---

## 🐛 常见问题速查

### Python 找不到
```bash
# 检查安装
python --version

# 如果失败,重新安装并勾选 "Add to PATH"
```

### pip 找不到
```bash
# 使用 Python 模块方式
python -m pip install -r requirements.txt
```

### OpenCV 安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重试
pip install opencv-python==4.8.1.78
```

### pywin32 导入失败
```bash
# 运行后安装脚本
python Scripts/pywin32_postinstall.py -install
```

### VC++ DLL 错误
```bash
# 下载安装
https://aka.ms/vs/17/release/vc_redist.x64.exe
```

### Comet Browser 找不到
```bash
# 检查是否已安装
dir "C:\Users\%USERNAME%\AppData\Local\Perplexity\Comet\Application\comet.exe"

# 如果不存在,从官网下载
```

### 端口 5000 被占用
```bash
# 查找占用进程
netstat -ano | findstr :5000

# 关闭进程
taskkill /PID <PID> /F
```

---

## 🎯 配置检查清单

快速检查您的环境:

```bash
# 1. Python 版本 (应为 3.9-3.11)
python --version

# 2. pip 可用
pip --version

# 3. 项目已克隆
cd comet-taskrunner

# 4. 依赖已安装
pip list | findstr flask

# 5. Comet Browser 已安装
where comet.exe
# 或检查默认路径
dir "C:\Users\%USERNAME%\AppData\Local\Perplexity\Comet\Application\comet.exe"

# 6. VC++ 已安装 (通常已包含在 Windows 10/11)
# 如有问题才需要安装
```

---

## 📞 获取帮助

如果遇到问题:

1. **查看完整文档**: [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
2. **查看项目 README**: [README.md](README.md)
3. **查看构建指南**: [BUILD_GUIDE.md](BUILD_GUIDE.md)
4. **提交 Issue**: GitHub Issues

---

## 🚀 开始使用

环境配置完成后:

1. **启动项目**
   ```bash
   start.bat
   ```

2. **测试 API**
   - 导入 Postman Collection: `api-spec/Comet_TaskRunner_Collection.postman_collection.json`
   - 参考: `api-spec/QUICK_START_CN.md`

3. **开发新功能**
   - 查看 `docs/` 了解架构
   - 参考 `src/tasks/` 了解任务组件

---

**保存此页面作为快速参考!** 📌

---

*最后更新: 2025-12-01*
