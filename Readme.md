# 机加工车间物料与生产管理系统部署

## 1.部署前置条件

* python :`V3.14.5`
* node: `V24.15.0`
* mongod: `V8.2.9`

## 2.部署方案

### 方案一：Docker Desktop（推荐，一键部署）

#### 1. 安装依赖

- 安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- 确保 WSL2 已启用（Docker Desktop 安装向导会自动处理）

#### 2. 配置环境变量

```she
# 在项目根目录创建 .env 文件
cp .env.example .env
```

编辑 `.env`：

```shell
MONGO_URI=mongodb://mongodb:27017/nkserp
JWT_SECRET=自行生成一个随机密钥
CORS_ORIGINS=*
```

启动

```shell
#cd NKSerp的目录
docker compose up -d
```

访问 `http://localhost`  本机IP即可使用。

常用命令

```shell
docker compose down          # 停止
docker compose up -d --build # 重新构建并启动
docker compose logs -f       # 查看日志
```

### 方案二：手动部署（开发/测试用）

安装 MongoDBV8.2.9

下载安装 [MongoDB Community Server](https://www.mongodb.com/try/download/community)，选择 Windows MSI 版本。安装时勾选 **Install MongoD as a Service**。

安装 Python3.14.5

```shell
cd C:\Users\HWnepstar\Desktop\NKSerp\backend
pip install -r requirements.txt
```

安装 Node.jsV24.15.0

下载安装 [Node.js 24 LTS](https://nodejs.org/)。

```shell
cd C:\Users\HWnepstar\Desktop\NKSerp\frontend
npm install
```

配置环境变量

设置 Windows 系统环境变量或在终端中：

```
set MONGO_URI=mongodb://127.0.0.1:27017/nkserp
set JWT_SECRET=自行生成一个随机密钥
set CORS_ORIGINS=*
```

启动后端

```
cd C:\Users\HWnepstar\Desktop\NKSerp\backend
python main.py
```

后端运行在 `http://localhost:8000`，API 文档在 `http://localhost:8000/docs`。

启动前端

```
cd C:\Users\HWnepstar\Desktop\NKSerp\frontend
npm run dev
```

前端运行在 `http://localhost`（Vite 配置了端口 80，自动代理 `/api` 到后端 8000）。

### 方案三：生产部署（IIS + NSSM）

适合需要开机自启、后台运行的场景。

后端：使用 NSSM 注册为 Windows 服务

1. 下载 [NSSM](https://nssm.cc/download)
2. 以管理员权限运行：

```
nssm install NKSerpBackend
```

在弹出的界面中设置：

- **Path**: `python.exe` 的完整路径
- **Startup directory**: `C:\Users\HWnepstar\Desktop\NKSerp\backend`
- **Arguments**: `-m uvicorn app.main:app --host 0.0.0.0 --port 8000`

*注意：需要将 `backend/main.py` 的 `reload=True` 改为 `reload=False`。*

前端：生产构建 + 任意静态服务器

```shell
cd C:\Users\HWnepstar\Desktop\NKSerp\frontend
npm run build
```

生成的 `dist/` 目录可以用以下方式部署：

- **IIS**：新建站点指向 `dist/`，添加 URL 重写规则（SPA fallback），配置反向代理 `/api` → `http://127.0.0.1:8000`
- **nginx for Windows**：用项目自带的 `nginx.conf`（把 `backend` 改为 `127.0.0.1`）
- **简捷方式**：`npm run preview` 或 `npx serve dist`