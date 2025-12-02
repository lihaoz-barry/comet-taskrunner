# 环境变量配置指南 (.env)

本文档详细解释 Comet Task Runner 的环境变量配置机制，以及如何确保 `backend.exe` 安全运行。

---

## 1. 核心概念

### 什么是环境变量？
环境变量是操作系统级别的键值对配置。它们允许我们在不修改代码的情况下改变程序的行为（例如设置密码、路径）。

### 为什么需要 .env 文件？
在开发和部署中，直接设置系统环境变量比较麻烦（需要重启终端、命令繁琐）。`.env` 文件是一个简单的文本文件，程序启动时会自动读取它，并将其中的内容"假装"成环境变量。

---

## 2. 文件说明

### `.env.example` (模板文件)
- **作用**: 告诉用户"你需要配置哪些变量"。
- **内容**: 包含变量名和示例值（通常是假的）。
- **Git 状态**: ✅ **会被 Push 到 GitHub**。
- **使用方法**: 用户下载代码后，复制此文件。

### `.env` (真实配置文件)
- **作用**: 存储您的**真实**密码和配置。
- **内容**: `COMET_API_KEY=真正的高强度密码`
- **Git 状态**: ❌ **绝不能 Push 到 GitHub** (已被 `.gitignore` 忽略)。
- **使用方法**: 程序启动时读取此文件。

---

## 3. 如何使用 (用户视角)

### 步骤 1: 准备配置文件
在项目根目录（或 `backend.exe` 同级目录）：
1. 找到 `.env.example` 文件。
2. 复制一份，重命名为 `.env`。
3. 用记事本打开 `.env`，修改密码：
   ```ini
   # 修改前
   COMET_API_KEY=change-me-to-a-secure-password
   
   # 修改后
   COMET_API_KEY=MySecretPassword123!
   ```
4. 保存文件。

### 步骤 2: 运行程序
双击 `backend.exe` (或 `start.bat`)。

**程序内部逻辑**:
1. 程序启动。
2. 执行 `load_dotenv()`: 寻找同目录下的 `.env` 文件。
3. 如果找到，将其内容加载到内存中。
4. 程序检查 `os.environ.get('COMET_API_KEY')`。
   - 如果找到了 (来自系统设置 或 .env): ✅ **启动成功**。
   - 如果没找到: ❌ **报错并退出**。

---

## 4. 报错机制演示

如果用户**没有**配置 `.env`，也没有设置系统环境变量，直接运行 `backend.exe`，会看到如下错误：

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
CRITICAL SECURITY ERROR: COMET_API_KEY environment variable is not set!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

To securely expose the server to the network, you MUST set an API Key.

[Option 1] Temporary (Current Session):
  set COMET_API_KEY=my-secret-password-123

[Option 2] Permanent (User Environment):
  setx COMET_API_KEY "my-secret-password-123"

[Option 3] .env file (Recommended for Dev):
  Create a .env file with: COMET_API_KEY=my-secret-password-123

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

程序会**立即退出** (Exit Code 1)，防止在不安全的状态下运行。

---

## 5. 常见问题 (FAQ)

### Q: 我修改了 .env，需要重启 backend.exe 吗？
**A**: **需要**。`.env` 文件只在程序启动的一瞬间被读取。

### Q: 如果我同时设置了系统环境变量和 .env，哪个生效？
**A**: 通常**系统环境变量优先**。如果系统里设置了 `KEY=A`，`.env` 里写了 `KEY=B`，程序会使用 `A`。这允许你在生产环境覆盖本地配置。

### Q: backend.exe 能找到 .env 吗？
**A**: **能**。只要 `.env` 文件和 `backend.exe` 在同一个文件夹里。我们在代码中使用了 `python-dotenv` 库，并已将其打包进 exe 中。

---

## 6. 最佳实践总结

1.  **开发者**:
    - 永远不要把真实密码写在代码里。
    - 永远不要把 `.env` 提交到 Git。
    - 始终维护 `.env.example` 以便他人知道如何配置。

2.  **部署者 (用户)**:
    - 下载 `backend.exe` 和 `.env.example`。
    - 创建 `.env` 并填入密码。
    - 运行 `backend.exe`。

---
**文档版本**: 1.0
**最后更新**: 2025-12-02
