# BiliNote 本地启动说明

本文档用于在本机手动启动 BiliNote 的后端和前端。

## 端口

- 后端：`http://localhost:8483`
- 前端：`http://localhost:3015`

## 启动后端

在项目根目录执行：

```powershell
cd backend
.\.venv\Scripts\python.exe main.py
```

如果没有虚拟环境或依赖不完整，先执行：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

后端启动成功后，终端一般会看到类似输出：

```text
Uvicorn running on http://0.0.0.0:8483
```

## 启动前端

另开一个 PowerShell 窗口，在项目根目录执行：

```powershell
cd BillNote_frontend
corepack pnpm install
corepack pnpm dev
```

如果 `pnpm install` 提示构建脚本被拦截，例如 `esbuild` 或 `core-js`，执行：

```powershell
corepack pnpm approve-builds --all
corepack pnpm install
corepack pnpm dev
```

前端启动成功后，终端一般会看到类似输出：

```text
Local: http://localhost:3015/
```

## 检查端口占用

如果启动失败，可以检查端口是否已经被占用：

```powershell
Get-NetTCPConnection -LocalPort 8483,3015 -ErrorAction SilentlyContinue |
  Select-Object LocalAddress,LocalPort,State,OwningProcess
```

根据 PID 查看进程：

```powershell
Get-Process -Id <PID>
```

停止某个进程：

```powershell
Stop-Process -Id <PID>
```

## 常见问题

### PowerShell 无法运行 npm 或 pnpm

如果遇到类似 `npm.ps1 cannot be loaded because running scripts is disabled`，优先使用：

```powershell
corepack pnpm dev
```

或者使用 `.cmd` 后缀：

```powershell
npm.cmd --version
```

### 前端不需要 Python 虚拟环境

前端依赖安装在 `BillNote_frontend/node_modules` 中，不需要像 Python 一样激活 `.venv`。

如果需要隔离 Node.js 版本，可以额外使用 `nvm-windows`、Volta 或 fnm。

