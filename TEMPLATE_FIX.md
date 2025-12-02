# Template Not Found Fix - 模板文件找不到修复

## 🐛 问题描述

### 错误信息
```
[ WARN:0@23.611] global loadsave.cpp:275 cv::findDecoder imread_('C:\Users\Barry\AppData\Local\Temp\templates\comet_Assistant_Unactive.png'): can't open/read file: check file path/integrity
2025-12-02 00:05:09,890 - automation.pattern_matcher - ERROR - Failed to load template: C:\Users\Barry\AppData\Local\Temp\templates\comet_Assistant_Unactive.png
```

### 问题原因

当运行 **打包后的 `backend.exe`** (PyInstaller) 时，程序无法找到模板文件。

**根本原因**:
1. `backend.spec` 中的 `templates` 目录被注释掉，没有打包进 exe
2. `ai_task.py` 的路径逻辑不支持 PyInstaller 的临时目录 (`_MEIPASS`)

### 影响范围
- ✅ **开发模式** (`python src/backend.py`) - 正常工作
- ❌ **打包版本** (`dist/backend.exe`) - 模板文件找不到

---

## ✅ 解决方案

### 修复 1: backend.spec (打包配置)

**文件**: `backend.spec`

**修改前**:
```python
datas=[
    # Include templates directory if it exists
    # ('templates', 'templates'),  # ← 被注释了
],
```

**修改后**:
```python
datas=[
    # Include templates directory for AI automation
    ('templates', 'templates'),  # ← 取消注释
    # Include screenshots directory (create if doesn't exist)
],
```

**说明**: 这确保 `templates/` 文件夹及其内容被打包进 exe

---

### 修复 2: ai_task.py (路径检测)

**文件**: `src/tasks/ai_task.py`

**修改内容**: 在 `__init__` 方法中添加 PyInstaller 检测

**核心逻辑**:
```python
# Check if running as PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller exe - use _MEIPASS
    base_path = Path(sys._MEIPASS)
    self.template_dir = base_path / "templates"
else:
    # Running in development mode - use relative path
    self.template_dir = Path(__file__).parent.parent.parent / "templates"
```

**原理**:
- `sys.frozen`: PyInstaller 设置的标志
- `sys._MEIPASS`: PyInstaller 解压文件的临时目录路径
- 开发模式: 使用相对路径 `../../templates`
- Exe 模式: 使用 `_MEIPASS/templates`

**额外改进**:
1. Screenshot 目录放在 exe 旁边，不在临时目录
2. 添加模板目录验证日志
3. 增加详细的调试信息

---

## 🔨 重新构建步骤

### 1. 确认修改已完成
```bash
# 检查 backend.spec
cat backend.spec | findstr "templates"
# 应该看到: ('templates', 'templates'),

# 检查模板文件存在
dir templates\comet_Assistant_Unactive.png
```

### 2. 重新构建 backend.exe
```bash
# 运行构建脚本
build_backend.bat

# 或手动构建
pip install pyinstaller
pyinstaller backend.spec
```

### 3. 验证打包结果
构建完成后，应该看到:
```
dist/
  └── backend.exe  (约 120-180MB)
```

### 4. 测试打包后的 exe
```bash
# 启动 backend.exe
cd dist
backend.exe
```

**预期日志输出**:
```
AITask created with instruction: ...
Template directory: C:\Users\Barry\AppData\Local\Temp\_MEI12345\templates
Screenshot directory: C:\...\dist\screenshots
✓ Template directory verified: C:\Users\Barry\AppData\Local\Temp\_MEI12345\templates
```

**关键点**:
- ✅ 看到 "Running as packaged exe, using _MEIPASS"
- ✅ 看到 "✓ Template directory verified"
- ✅ 没有 "Template directory not found" 错误

---

## 🧪 完整测试流程

### Test 1: 开发模式 (Python)
```bash
# 确保开发模式仍然工作
python src/backend.py

# 在另一个终端测试 AI 任务
curl -X POST http://127.0.0.1:5000/execute/ai ^
  -H "Content-Type: application/json" ^
  -d "{\"instruction\":\"/ikea\"}"
```

### Test 2: 打包模式 (Exe)
```bash
# 启动打包后的 exe
dist\backend.exe

# 在另一个终端测试同样的 AI 任务
curl -X POST http://127.0.0.1:5000/execute/ai ^
  -H "Content-Type: application/json" ^
  -d "{\"instruction\":\"/ikea\"}"
```

### Test 3: 检查日志
查看终端输出，确认:
- ✅ 模板目录路径正确
- ✅ 模板文件加载成功
- ✅ 没有 OpenCV 警告

---

## 📊 修复前后对比

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| **开发模式** | ✅ 正常 | ✅ 正常 |
| **打包 exe** | ❌ 模板找不到 | ✅ 正常 |
| **Template 路径** | 总是相对路径 | 自动检测环境 |
| **Screenshot 位置** | 临时目录 | exe 旁边 (持久化) |
| **调试信息** | 最小 | 详细日志 |

---

## 🔍 验证清单

构建和部署前请确认:

- [ ] `backend.spec` 中 `templates` 已取消注释
- [ ] `ai_task.py` 包含 PyInstaller 检测代码
- [ ] 模板文件存在于 `templates/` 目录
  - [ ] `comet_Assistant_Unactive.png`
  - [ ] `comet_input_box.png`
- [ ] 运行 `build_backend.bat` 成功
- [ ] `dist/backend.exe` 文件大小正常 (120-180MB)
- [ ] 启动 exe 看到 "✓ Template directory verified" 日志
- [ ] AI 任务可以正常执行
- [ ] 没有 OpenCV 加载模板错误

---

## 🐛 常见问题

### Q1: 重新构建后仍然找不到模板
**A**: 
```bash
# 清理旧的构建文件
rmdir /s /q build dist

# 重新构建
pyinstaller backend.spec --clean
```

### Q2: 看到 "Template directory not found" 错误
**A**: 检查:
```bash
# 1. 模板文件确实存在
dir templates\*.png

# 2. backend.spec 正确配置
findstr /c:"('templates', 'templates')" backend.spec

# 3. 重新构建
build_backend.bat
```

### Q3: exe 文件太大
**A**: 这是正常的，因为包含了:
- Python 解释器
- 所有依赖库 (OpenCV, NumPy, Flask 等)
- 模板图片文件

大小约 120-180MB 是预期的。

### Q4: 想在其他位置使用自定义模板
**A**: 
```python
# 创建 AITask 时指定模板目录
task = AITask(
    instruction="/ikea",
    template_dir="C:/my/custom/templates"
)
```

---

## 📝 技术细节

### PyInstaller 打包原理

当运行打包后的 exe:
1. Exe 解压到临时目录: `C:\Users\...\AppData\Local\Temp\_MEIxxxxx\`
2. `sys._MEIPASS` 指向这个临时目录
3. 所有 `datas` 中的文件被放在 `_MEIPASS` 下

### 为什么 Screenshot 不在临时目录?

**原因**: 临时目录在程序退出后会被删除，截图应该持久保存。

**解决**: Screenshot 目录放在 exe 所在目录:
```python
exe_dir = Path(sys.executable).parent
self.screenshot_dir = exe_dir / "screenshots"
```

---

## ✅ 总结

### 问题
打包后的 `backend.exe` 找不到模板文件

### 根本原因
1. 模板没有被打包进 exe
2. 路径逻辑不支持 PyInstaller

### 解决方案
1. 修复 `backend.spec` - 包含 templates
2. 修复 `ai_task.py` - 自动检测环境

### 后续步骤
1. 重新构建: `build_backend.bat`
2. 测试 exe: `dist\backend.exe`
3. 确认日志正常

---

**修复日期**: 2025-12-02  
**修复版本**: v0.2.1  
**影响文件**: `backend.spec`, `ai_task.py`  
**测试状态**: ✅ 待验证
