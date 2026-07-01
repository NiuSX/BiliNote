# BiliNote 项目目录结构说明

本文档用于说明当前仓库的整体结构、各目录职责、核心调用链路以及开发/部署时最常用的入口文件。

## 一、项目定位

BiliNote 是一个 AI 视频笔记生成工具。用户提交 Bilibili、YouTube、抖音、快手、小宇宙或本地视频链接后，系统会完成视频/音频下载、字幕获取或语音转写、LLM 总结、Markdown 笔记生成、思维导图展示，以及基于笔记和转写内容的 RAG 问答。

项目由以下几部分组成：


- `backend/`：FastAPI 后端，负责下载、转写、LLM 调用、任务状态、数据库、导出、RAG 问答。
- `BillNote_frontend/`：React + Vite Web 前端，也可通过 Tauri 打包桌面端。
- `BillNote_extension/`：Vue 3 浏览器扩展，用于从当前网页一键提交视频生成笔记。
- `nginx/`：Docker 部署时的反向代理配置。
- `doc/`：项目展示图片、二维码和文档素材。
- 根目录 Docker/说明文件：用于本地开发、容器部署、版本发布和贡献说明。

## 二、根目录结构

```text
BiliNote/
├── backend/                         # FastAPI 后端服务
├── BillNote_frontend/               # React Web 前端与 Tauri 桌面壳
├── BillNote_extension/              # 浏览器扩展，复用同一个后端 API
├── doc/                             # README 和文档使用的图片素材
├── nginx/                           # Nginx 反向代理配置
├── .github/                         # GitHub Actions / Issue 模板等项目自动化配置
├── .vscode/                         # VS Code 工作区配置
├── .idea/                           # JetBrains IDE 本地配置
├── .env                             # 本地实际环境变量，包含端口、目录、镜像源等
├── .env.example                     # 环境变量示例
├── .gitignore                       # Git 忽略规则
├── docker-compose.yml               # 默认 Docker Web 部署编排
├── docker-compose.gpu.yml           # GPU 版本 Docker 编排
├── Dockerfile.complete              # 一体化镜像构建文件
├── run.bat                          # Windows 快速启动脚本
├── README.md                        # 项目介绍和使用说明
├── CHANGELOG.md                     # 版本变更记录
├── CONTRIBUTING.md                  # 贡献指南
├── RELEASING.md                     # 发布流程说明
├── CLAUDE.md                        # 给代码助手/协作者的项目约定
└── PROJECT_STRUCTURE_CN.md          # 本文件：中文目录结构说明
```

## 三、后端目录结构

```text
backend/
├── main.py                          # 后端进程入口：加载 env、初始化目录、注册中间件和静态资源
├── ffmpeg_helper.py                 # 启动期检查 FFmpeg 是否可用
├── requirements.txt                 # pip 依赖
├── pyproject.toml                   # Python 项目配置
├── build.sh / build.bat             # PyInstaller 后端桌面端打包脚本
├── Dockerfile / Dockerfile.gpu      # CPU/GPU 后端镜像构建文件
├── app/
│   ├── __init__.py                  # FastAPI app 工厂，统一挂载 API router
│   ├── routers/                     # HTTP API 层，只做请求校验、编排和响应封装
│   │   ├── note.py                  # 笔记生成、上传、任务状态、图片代理
│   │   ├── provider.py              # LLM 供应商配置 CRUD
│   │   ├── model.py                 # 模型列表与启用状态管理
│   │   ├── config.py                # 系统、下载器、转写器等运行配置
│   │   └── chat.py                  # RAG 问答索引和提问接口
│   ├── services/                    # 业务服务层
│   │   ├── note.py                  # NoteGenerator，视频笔记生成主流水线
│   │   ├── task_serial_executor.py  # 后台任务线程池执行器，导出名保留 serial 兼容旧代码
│   │   ├── provider.py              # LLM 供应商业务逻辑
│   │   ├── model.py                 # 模型业务逻辑
│   │   ├── cookie_manager.py        # 各平台 Cookie 持久化
│   │   ├── proxy_config_manager.py  # 下载代理配置
│   │   ├── transcriber_config_manager.py # 转写器类型、模型大小和下载状态管理
│   │   ├── vector_store.py          # ChromaDB 向量索引，供笔记问答检索
│   │   ├── chat_service.py          # RAG + Tool Calling 问答编排
│   │   └── chat_tools.py            # Chat 可调用工具：查转写、查视频信息、查完整笔记
│   ├── downloaders/                 # 不同平台下载适配层
│   │   ├── base.py                  # Downloader 抽象基类
│   │   ├── bilibili_downloader.py   # Bilibili 下载、字幕和元数据适配
│   │   ├── youtube_downloader.py    # YouTube 下载和字幕适配
│   │   ├── douyin_downloader.py     # 抖音下载适配
│   │   ├── kuaishou_downloader.py   # 快手下载适配
│   │   ├── local_downloader.py      # 本地上传文件适配
│   │   └── *_subtitle.py / *_helper # 平台字幕、签名、补丁等辅助逻辑
│   ├── transcriber/                 # 语音转写引擎
│   │   ├── base.py                  # 转写器抽象接口
│   │   ├── transcriber_provider.py  # 根据配置选择转写器
│   │   ├── whisper.py               # fast-whisper 转写
│   │   ├── groq.py                  # Groq 云端转写
│   │   ├── bcut.py                  # 必剪字幕能力
│   │   ├── kuaishou.py              # 快手字幕能力
│   │   ├── mlx_whisper_transcriber.py # Apple Silicon MLX Whisper
│   │   └── model_download_state.py  # 本地模型下载状态
│   ├── gpt/                         # LLM 适配层
│   │   ├── base.py                  # GPT 抽象接口
│   │   ├── gpt_factory.py           # 根据模型配置创建 GPT 实例
│   │   ├── universal_gpt.py         # OpenAI 兼容协议的统一实现
│   │   ├── request_chunker.py       # 长转写分块与断点续写
│   │   ├── prompt.py                # Prompt 模板
│   │   ├── prompt_builder.py        # Prompt 组装器
│   │   ├── tools.py                 # LLM 工具定义
│   │   └── provider/                # OpenAI 兼容客户端封装
│   ├── db/                          # SQLite + SQLAlchemy 数据访问层
│   │   ├── engine.py                # 数据库 engine/session
│   │   ├── init_db.py               # 初始化表结构和内置数据
│   │   ├── *_dao.py                 # DAO：provider/model/video_task
│   │   ├── builtin_providers.json   # 默认 LLM 供应商
│   │   └── models/                  # SQLAlchemy 表模型
│   ├── models/                      # Pydantic / dataclass 业务数据模型
│   ├── enmus/                       # 枚举定义（目录名沿用项目历史拼写）
│   ├── validators/                  # URL 和平台校验
│   ├── utils/                       # 通用工具：响应封装、截图、导出、日志、视频读取
│   ├── exceptions/                  # 业务异常和 FastAPI 异常处理器
│   ├── decorators/                  # 装饰器工具
│   └── core/                        # 预留核心配置目录
├── events/                          # Blinker 事件系统，处理转写后清理等异步副作用
├── tests/                           # Pytest 测试用例
├── fonts/                           # 导出 PDF/DOCX 使用的字体
└── .env.example                     # 后端单独环境变量示例
```

## 四、前端目录结构

```text
BillNote_frontend/
├── package.json                     # React/Vite/Tauri 前端依赖与脚本
├── vite.config.ts                   # Vite 配置，开发时代理 /api 和 /static 到后端
├── tailwind.config.cjs              # Tailwind 配置
├── eslint.config.js                 # ESLint 配置
├── components.json                  # shadcn/ui 组件配置
├── Dockerfile                       # 前端容器构建文件
├── deploy/                          # 容器内 Nginx 启动和模板
├── public/                          # 静态资源
├── src/
│   ├── main.tsx                     # React 入口
│   ├── App.tsx                      # 应用路由、后端初始化门禁、Tauri/Web 路由切换
│   ├── pages/
│   │   ├── Index.tsx                # 主布局入口
│   │   ├── HomePage/                # 笔记生成主页面
│   │   │   ├── Home.tsx             # 首页布局
│   │   │   └── components/          # 表单、Markdown、思维导图、历史、聊天面板
│   │   ├── SettingPage/             # 模型、下载器、转写器、监控、关于页面
│   │   ├── Onboarding/              # 桌面端首次引导
│   │   └── NotFoundPage/            # 404 页面
│   ├── components/
│   │   ├── ui/                      # shadcn/ui 基础组件
│   │   ├── Form/                    # 模型和下载器配置表单
│   │   ├── BackendHealth/           # 后端健康状态和日志面板
│   │   ├── SystemDiagnostic/        # 启动诊断提示
│   │   ├── Icons/                   # 平台和供应商图标
│   │   └── Lottie/                  # 动画组件
│   ├── services/                    # Axios API 封装，与 backend/app/routers 对齐
│   ├── store/                       # Zustand 状态：任务、模型、供应商、配置、聊天
│   ├── hooks/                       # 任务轮询、后端初始化检查等 React Hook
│   ├── constant/                    # 笔记格式、风格、平台常量
│   ├── lib/                         # 通用工具和 markmap 适配
│   ├── utils/                       # Axios 实例、工具函数
│   ├── types/                       # 全局类型声明
│   └── assets/                      # 图片、SVG、Lottie JSON
└── src-tauri/                       # Tauri 2 桌面端配置和 Rust 壳
    ├── tauri.conf.json              # 桌面端窗口、权限和打包配置
    ├── Cargo.toml / Cargo.lock      # Rust 依赖
    ├── capabilities/                # Tauri 权限能力配置
    ├── icons/                       # 桌面端图标
    └── src/                         # Rust 主入口
```

## 五、浏览器扩展目录结构

```text
BillNote_extension/
├── package.json                     # Vue 扩展依赖与脚本
├── vite.config*.mts                 # popup/options/background/content 构建配置
├── unocss.config.ts                 # UnoCSS 配置
├── playwright.config.ts             # e2e 测试配置
├── scripts/                         # manifest 生成和构建准备脚本
├── e2e/                             # Playwright e2e
├── src/
│   ├── manifest.ts                  # MV3 manifest 源文件，构建时生成 manifest.json
│   ├── popup/                       # 浏览器按钮弹窗，一键生成笔记
│   ├── options/                     # 扩展设置页：后端地址、模型、画质、Cookie 等
│   ├── sidepanel/                   # 侧边栏：展示笔记、思维导图、问答
│   ├── background/                  # MV3 service worker
│   ├── contentScripts/              # 内容脚本占位和页面注入能力
│   ├── logic/                       # API、存储、平台识别、字幕抓取等核心逻辑
│   ├── components/                  # Vue 组件：Markdown、MindMap、Chat、进度等
│   ├── composables/                 # WebExtension storage hook
│   ├── styles/                      # 全局样式
│   └── assets/                      # 扩展图标等资源
└── extension/                       # 构建输出目录，加载到浏览器的 unpacked extension
```

## 六、核心业务调用链路

### 1. Web 前端生成笔记

```text
NoteForm.tsx
  -> services/note.ts: generateNote()
  -> backend/app/routers/note.py: POST /api/generate_note
  -> 写入 PENDING 状态文件
  -> BackgroundTasks 调用 run_note_task()
  -> task_serial_executor.run()
  -> NoteGenerator.generate()
  -> Downloader 获取字幕/下载音视频
  -> Transcriber 转写音频（没有平台字幕时）
  -> GPTFactory + UniversalGPT 生成 Markdown
  -> 截图/视频链接后处理
  -> 保存 note_results/{task_id}.json
  -> VectorStoreManager 建立 RAG 索引
  -> 前端 useTaskPolling 轮询 /api/task_status/{task_id}
```

### 2. 浏览器扩展生成笔记

```text
Popup.vue
  -> detectPlatform() 判断当前 tab 是否支持
  -> Bilibili 可在浏览器侧 fetchBilibiliSubtitle() 预取字幕
  -> logic/api.ts: generateNote()
  -> 后端 /api/generate_note
  -> prefetched_transcript 写入 {task_id}_transcript.json
  -> NoteGenerator 命中转写缓存，跳过字幕下载/音频转写
  -> Popup 和 Sidepanel 轮询/展示结果
```

### 3. AI 问答

```text
ChatPanel / extension ChatPanel
  -> /api/chat/index 建立或确认索引
  -> VectorStoreManager 将 meta、Markdown、transcript 写入 ChromaDB
  -> /api/chat/ask 提交问题
  -> chat_service 检索相关片段
  -> LLM 可调用 chat_tools 查询更多原文/元信息/完整笔记
  -> 返回 answer + sources
```

## 七、运行和部署入口

### 后端开发

```bash
cd backend
pip install -r requirements.txt
python main.py
```

默认监听 `0.0.0.0:8483`。

### 前端开发

```bash
cd BillNote_frontend
pnpm install
pnpm dev
```

默认监听 `3015`，开发代理将 `/api` 与 `/static` 转发到后端。

### 浏览器扩展开发

```bash
cd BillNote_extension
pnpm install
pnpm dev
```

构建输出在 `BillNote_extension/extension/`，浏览器扩展页选择“加载已解压的扩展程序”。

### Docker 部署

```bash
docker-compose up
```

默认包含 `backend`、`frontend`、`nginx` 三个服务。`nginx` 对外暴露 `.env` 中的 `APP_PORT`。

## 八、运行时重要目录

- `backend/note_results/`：任务状态、转写缓存、音频元信息缓存、最终笔记 JSON/Markdown。
- `backend/static/screenshots/`：生成笔记时插入的截图和视频理解拼图。
- `backend/uploads/`：本地视频上传文件。
- `backend/vector_db/`：ChromaDB 持久化向量索引。
- `backend/app/db/bili_note.db`：SQLite 数据库。
- `BillNote_extension/extension/`：扩展构建产物。

这些目录大多属于运行产物，通常不应提交到 Git。

## 九、配置关系

- 根目录 `.env` 被 Docker、后端和前端构建读取。
- LLM API Key 主要通过前端设置页写入数据库，不建议写死在代码里。
- 下载器 Cookie 通过后端配置接口保存，Bilibili/YouTube 等下载器会按平台读取。
- `FFMPEG_BIN_PATH` 可指定 FFmpeg 路径；未指定时使用系统 PATH。
- Docker 前端不直接访问后端容器端口，而是通过 `nginx/default.conf` 反向代理。

## 十、维护建议

- 新增平台时，优先实现 `backend/app/downloaders/base.py` 定义的下载器接口，并在 `SUPPORT_PLATFORM_MAP` 中注册。
- 新增转写器时，实现 `app/transcriber/base.py`，再在 `transcriber_provider.py` 注册。
- 新增 LLM 供应商时，优先保持 OpenAI 兼容协议，复用 `UniversalGPT` 和 `OpenAICompatibleProvider`。
- 前端新增 API 时，应先在 `backend/app/routers/` 明确响应结构，再在 `BillNote_frontend/src/services/` 或扩展 `src/logic/api.ts` 增加封装。
- 与任务状态相关的变更，需要同时检查后端 `TaskStatus`、状态文件写入、前端 `useTaskPolling` 和扩展 `poll()`。
