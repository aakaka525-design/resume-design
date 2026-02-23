# 猫步简历（个人本地版）

这是面向个人本地使用的简历项目。当前主流程聚焦两条链路：

- 简历编辑：`/resume` -> `/resumedetail/:id` -> `/designResume/:id`
- 积木编辑：`/legoTemplateList` -> `/legoDesigner`

说明：
- 当前前端主路由不依赖注册/登录页，默认走本地自动登录接口。
- 仓库中仍保留部分历史代码与素材，未在主流程中启用。

## 项目结构（单仓）

```text
resume-design/
├── frontend/    # Vue 前端
├── backend/     # FastAPI 后端
├── doc/         # 修复计划/日志/测试报告
└── scripts/     # 本地联调辅助脚本
```

## 运行要求

- Node.js 18+
- pnpm
- Python 3.10+
- pip

## 启动方式

以下命令默认都从仓库根目录 `resume-design/` 执行。

### 1) 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2) 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

前端默认请求 `http://localhost:8000`（见 `frontend/.env.development`）。

## 当前约束

- 仅本机访问（后端 `LOCAL_ONLY=true`）
- 免注册登录（通过 `/huajian/auth/autoLogin` 自动获取本地用户）
- 上传路径有目录穿越防护
- 简历/积木保存与读取带 owner 约束

## 常用验证命令

```bash
# 前端类型检查
cd frontend
pnpm exec vue-tsc --noEmit

# 前端 lint
pnpm exec eslint .

# 前端构建
pnpm build:dev

# 后端语法检查
cd ../backend
python3 -m py_compile main.py config.py deps.py routers/*.py models/*.py
```

## 本地联调探针

```bash
bash scripts/local_stack_probe.sh
```

## 文档记录

- `doc/local-backend-fix/PLAN.md`
- `doc/local-backend-fix/WORKLOG.md`
- `doc/local-backend-fix/TEST-REPORT.md`
