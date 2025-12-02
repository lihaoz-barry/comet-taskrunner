# Comet Task Runner - 完整环境配置指南

## 📋 目录

1. [Python 版本要求](#python-版本要求)
2. [系统要求](#系统要求)
3. [依赖清单](#依赖清单)
4. [全新环境配置步骤](#全新环境配置步骤)
5. [验证安装](#验证安装)
6. [常见问题](#常见问题)

---

## Python 版本要求

### ✅ 推荐版本
**Python 3.9 - 3.11**

### 版本说明
- **最低要求**: Python 3.8+
- **推荐**: Python 3.10 或 3.11
- **已测试**: Python 3.9, 3.10, 3.11
- **不支持**: Python 2.x, Python 3.7 及以下

### 为什么选择这些版本?
- Python 3.9+: 更好的类型注解支持
- Python 3.10/3.11: 性能优化,最佳兼容性
- 所有依赖库都完全支持这些版本

### 检查您的 Python 版本
```bash
python --version
# 或
python3 --version
```

### 如何安装 Python

#### Windows
1. 访问 [Python 官网](https://www.python.org/downloads/)
2. 下载 Python 3.10 或 3.11 安装程序
3. 安装时 **勾选** "Add Python to PATH"
4. 完成安装后重启终端

#### 验证安装
```bash
python --version
pip --version
```

预期输出:
```
Python 3.10.x (或 3.11.x)
pip 23.x.x from ...
```

---

## 系统要求

### 操作系统
- **Windows 10/11** (64-bit) ✅ 完全支持
- **Windows Server 2019+** ✅ 支持
- **其他系统**: 不支持 (项目使用 Windows 特定的 API)

### 其他要求
- **内存**: 最少 4GB RAM (推荐 8GB+)
- **磁盘空间**: 至少 500MB 可用空间
- **网络**: 需要互联网连接 (下载依赖、访问 API)

### 必需软件
1. **Comet Browser** (必须) 
   - 项目核心依赖
   - 下载: [Comet Browser 官网](https://www.perplexity.ai/hub/blog/comet-browser)
   
2. **Visual C++ Redistributable**
   - OpenCV 需要
   - 下载: https://aka.ms/vs/17/release/vc_redist.x64.exe

---

## 依赖清单

### Python 依赖包 (requirements.txt)

```txt
flask                  # Web 框架,后端 API 服务器
requests              # HTTP 客户端,前端调用后端
psutil                # 进程监控
opencv-python>=4.8.0  # 图像处理,模板匹配
numpy>=1.24.0         # 数值计算,OpenCV 依赖
mss>=9.0.0            # 屏幕截图
pyautogui>=0.9.50     # 鼠标键盘控制
Pillow>=10.0.0        # 图像处理
pywin32>=305          # Windows API 调用
```

### 详细说明

#### 1. **Flask** - 后端框架
- **用途**: REST API 服务器
- **版本**: 最新稳定版
- **文件**: `src/backend.py`
- **必需**: ✅ 后端

#### 2. **Requests** - HTTP 客户端
- **用途**: 前端与后端通信
- **版本**: 最新稳定版
- **文件**: `src/frontend.py`
- **必需**: ✅ 前端

#### 3. **psutil** - 进程监控
- **用途**: 监控浏览器进程状态
- **文件**: `src/tasks/base_task.py`
- **必需**: ✅ 核心功能

#### 4. **opencv-python** - 计算机视觉
- **用途**: 模板匹配,查找 UI 元素
- **版本**: >= 4.8.0
- **文件**: `src/automation/pattern_matcher.py`
- **必需**: ✅ AI 自动化

#### 5. **Numpy** - 数值计算
- **用途**: OpenCV 后端
- **版本**: >= 1.24.0
- **必需**: ✅ OpenCV 依赖

#### 6. **MSS** - 屏幕截图
- **用途**: 快速截屏
- **版本**: >= 9.0.0
- **文件**: `src/automation/screenshot.py`
- **必需**: ✅ AI 自动化

#### 7. **PyAutoGUI** - 自动化
- **用途**: 鼠标移动、点击、键盘输入
- **版本**: >= 0.9.50
- **文件**: `src/automation/mouse_controller.py`
- **必需**: ✅ AI 自动化

#### 8. **Pillow** - 图像处理
- **用途**: 图像格式转换
- **版本**: >= 10.0.0
- **必需**: ✅ 截图处理

#### 9. **pywin32** - Windows API
- **用途**: 窗口管理,进程查找
- **版本**: >= 305
- **文件**: `src/automation/window_manager.py`
- **必需**: ✅ Windows 集成

---

## 全新环境配置步骤

### 🚀 方案 A: 快速配置 (推荐)

使用项目自带的启动脚本,会自动检查和安装依赖。

```bash
# 1. 克隆或下载项目
cd C:\Users\YourName\Projects
git clone https://github.com/lihaoz-barry/comet-taskrunner.git
cd comet-taskrunner

# 2. 双击 start.bat 文件
# 脚本会自动:
#   - 检查 Python 安装
#   - 检查依赖并提示安装
#   - 启动后端和前端
```

**start.bat 脚本功能**:
- ✅ 自动检测 Python
- ✅ 检测 Comet Browser
- ✅ 提示安装缺失的依赖
- ✅ 启动前端和后端
- ✅ 选择最佳终端 (Windows Terminal / PowerShell / CMD)

---

### 🔧 方案 B: 手动配置 (完全控制)

#### 步骤 1: 安装 Python

```bash
# 下载并安装 Python 3.10 或 3.11
# 确保勾选 "Add Python to PATH"
```

#### 步骤 2: 验证 Python 安装

```bash
python --version
pip --version
```

#### 步骤 3: 克隆项目

```bash
cd C:\Users\YourName\Projects
git clone https://github.com/lihaoz-barry/comet-taskrunner.git
cd comet-taskrunner
```

#### 步骤 4: 创建虚拟环境 (可选但推荐)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# 如果 PowerShell 报错,先运行:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 步骤 5: 安装所有依赖

```bash
# 安装 requirements.txt 中的所有包
pip install -r requirements.txt

# 等待安装完成 (大约 2-5 分钟)
```

**可能的输出**:
```
Collecting flask
  Downloading flask-3.0.0-py3-none-any.whl (99 kB)
Collecting opencv-python>=4.8.0
  Downloading opencv_python-4.8.1.xx-cp310-cp310-win_amd64.whl (38.3 MB)
...
Successfully installed flask-3.0.0 opencv-python-4.8.1 ...
```

#### 步骤 6: 安装 Comet Browser

1. 访问 Comet Browser 官网或 Perplexity 下载页
2. 下载并安装
3. 记住安装路径 (通常在 `C:\Users\YourName\AppData\Local\Perplexity\Comet\`)

#### 步骤 7: 安装 Visual C++ Redistributable

```bash
# 下载并安装
https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### 步骤 8: 验证安装

```bash
# 测试导入所有模块
python -c "import flask, requests, psutil, cv2, numpy, mss, pyautogui, PIL, win32gui; print('✅ 所有依赖安装成功!')"
```

预期输出:
```
✅ 所有依赖安装成功!
```

---

## 验证安装

### 完整测试流程

#### 1. 测试 Python 环境

```bash
python -c "import sys; print(f'Python {sys.version}')"
```

#### 2. 测试所有依赖

```bash
# 创建测试脚本
python test_dependencies.py
```

**test_dependencies.py** (临时创建):
```python
import sys

print("Testing all dependencies...")
print("-" * 50)

dependencies = [
    ("flask", "Flask"),
    ("requests", "Requests"),
    ("psutil", "psutil"),
    ("cv2", "OpenCV"),
    ("numpy", "NumPy"),
    ("mss", "MSS"),
    ("pyautogui", "PyAutoGUI"),
    ("PIL", "Pillow"),
    ("win32gui", "pywin32"),
]

failed = []
for import_name, display_name in dependencies:
    try:
        __import__(import_name)
        print(f"✅ {display_name:15} - OK")
    except ImportError as e:
        print(f"❌ {display_name:15} - FAILED: {e}")
        failed.append(display_name)

print("-" * 50)
if failed:
    print(f"\n❌ Failed: {', '.join(failed)}")
    print("\nRun: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✅ All dependencies installed successfully!")
    sys.exit(0)
```

#### 3. 测试后端

```bash
# 启动后端
python src/backend.py
```

预期输出:
```
============================================================
Starting Comet Task Runner Backend
============================================================
✓ TaskQueue initialized with Comet path: C:\...\comet.exe
URL Task API: POST /execute/url
AI Task API:  POST /execute/ai
============================================================
 * Running on http://127.0.0.1:5000
```

在另一个终端测试:
```bash
curl http://127.0.0.1:5000/health
```

预期响应:
```json
{"status":"ok","message":"Comet Task Runner is running"}
```

#### 4. 测试前端

```bash
# 在新终端启动前端 (后端保持运行)
python src/frontend.py
```

应该看到 Tkinter GUI 窗口打开。

#### 5. 测试完整流程

1. 在 GUI 中点击 "Execute" 执行一个 URL
2. 观察 Comet Browser 是否打开
3. 检查任务状态是否变为 "Done"

---

## 常见问题

### 问题 1: pip 命令找不到

**症状**:
```
'pip' is not recognized as an internal or external command
```

**解决方案**:
```bash
# 使用 Python 模块方式运行 pip
python -m pip install -r requirements.txt

# 或者修复 PATH
# 重新安装 Python,确保勾选 "Add Python to PATH"
```

---

### 问题 2: OpenCV 安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement opencv-python
```

**解决方案**:
```bash
# 方案 1: 升级 pip
python -m pip install --upgrade pip

# 方案 2: 使用预编译版本
pip install opencv-python --only-binary :all:

# 方案 3: 安装特定版本
pip install opencv-python==4.8.1.78
```

---

### 问题 3: pywin32 安装后无法导入

**症状**:
```python
ImportError: DLL load failed while importing win32gui
```

**解决方案**:
```bash
# 运行 pywin32 后安装脚本
python Scripts/pywin32_postinstall.py -install

# 或重新安装
pip uninstall pywin32
pip install pywin32
```

---

### 问题 4: Visual C++ 错误

**症状**:
```
ImportError: DLL load failed: The specified module could not be found
```

**解决方案**:
```bash
# 安装 Visual C++ Redistributable
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# Windows 10/11 通常已包含,但可能需要更新
```

---

### 问题 5: Comet Browser 找不到

**症状**:
```
Comet browser not found in registry or fallback location
```

**解决方案**:

方案 1: 安装 Comet Browser
```bash
# 从官网下载安装
# https://www.perplexity.ai/hub/blog/comet-browser
```

方案 2: 手动配置路径
```python
# 编辑 src/backend.py
# 找到 fallback_path,修改为您的 Comet 安装路径
fallback_path = r"C:\Your\Custom\Path\comet.exe"
```

---

### 问题 6: 虚拟环境 PowerShell 激活失败

**症状**:
```
cannot be loaded because running scripts is disabled on this system
```

**解决方案**:
```powershell
# 在 PowerShell (管理员模式) 运行:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 然后重新激活虚拟环境
venv\Scripts\Activate.ps1
```

---

### 问题 7: 端口 5000 被占用

**症状**:
```
OSError: [WinError 10048] Only one usage of each socket address is normally permitted
```

**解决方案**:

方案 1: 查找占用端口的进程并关闭
```bash
# 查找占用 5000 端口的进程
netstat -ano | findstr :5000

# 关闭进程 (使用上面找到的 PID)
taskkill /PID <PID> /F
```

方案 2: 修改后端端口
```python
# 编辑 src/backend.py
# 最后一行修改端口
app.run(host='127.0.0.1', port=5001, debug=False)

# 同时修改 src/frontend.py
BACKEND_URL = "http://127.0.0.1:5001"
```

---

## 📊 依赖版本兼容性表

| Python 版本 | Flask | OpenCV | PyAutoGUI | pywin32 | 状态 |
|------------|-------|--------|-----------|---------|------|
| 3.8        | ✅    | ✅     | ✅        | ✅      | 支持 |
| 3.9        | ✅    | ✅     | ✅        | ✅      | ✅ 推荐 |
| 3.10       | ✅    | ✅     | ✅        | ✅      | ✅ 最佳 |
| 3.11       | ✅    | ✅     | ✅        | ✅      | ✅ 最新 |
| 3.12       | ⚠️    | ⚠️     | ⚠️        | ⚠️      | 未测试 |

---

## 🎯 快速故障排查

```bash
# 1. 检查 Python 版本
python --version

# 2. 检查 pip 版本
pip --version

# 3. 升级 pip
python -m pip install --upgrade pip

# 4. 重新安装所有依赖
pip install -r requirements.txt --force-reinstall

# 5. 测试依赖
python -c "import flask, requests, psutil, cv2, numpy, mss, pyautogui, PIL, win32gui"

# 6. 运行后端测试
python src/backend.py

# 7. 在新终端测试健康检查
curl http://127.0.0.1:5000/health
```

---

## 📝 环境配置检查清单

使用此清单确保环境完整配置:

- [ ] Python 3.9+ 已安装
- [ ] Python 已添加到 PATH
- [ ] pip 可以正常运行
- [ ] 已安装 Visual C++ Redistributable
- [ ] Comet Browser 已安装
- [ ] 已克隆/下载项目代码
- [ ] 已运行 `pip install -r requirements.txt`
- [ ] 所有依赖导入测试通过
- [ ] 后端可以启动 (5000 端口)
- [ ] 健康检查返回 OK
- [ ] 前端 GUI 可以打开
- [ ] 可以成功执行 URL 任务

---

## 🚀 下一步

环境配置完成后:

1. **阅读项目文档**
   - [README.md](README.md) - 项目概述
   - [BUILD_GUIDE.md](BUILD_GUIDE.md) - 打包指南

2. **测试 API**
   - 导入 Postman Collection
   - 参考 [api-spec/README.md](api-spec/README.md)

3. **开始开发**
   - 查看 `docs/` 目录了解架构
   - 阅读任务组件代码 `src/tasks/`

---

**文档版本**: 1.0  
**最后更新**: 2025-12-01  
**维护者**: Barry
