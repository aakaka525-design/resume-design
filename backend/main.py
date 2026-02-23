import ipaddress
import secrets

import bcrypt as _bcrypt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import (
    ALLOW_AUTO_LOGIN,
    DEFAULT_LOCAL_EMAIL,
    LOCAL_ONLY,
    UPLOAD_DIR,
)
from database import init_db
from deps import create_token
from utils import api_response

# 导入最小路由集合
from routers.users import router as users_router
from routers.common import router as common_router
from routers.resume import router as resume_router
from routers.user_resume import router as user_resume_router
from routers.create_template import router_user
from routers.lego import router_lego, router_template
from routers.upload import router as upload_router
from routers.integral import router as integral_router
from routers.pdf import router as pdf_router
from routers.lego_pdf import router as lego_pdf_router

app = FastAPI(
    title="本地简历编辑器后端",
    description="仅用于本地个人项目的最小 API（简历编辑 + 积木编辑）",
    version="1.0.0",
)

# CORS 配置 — 允许本地前端开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 个人使用，允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册最小路由
app.include_router(users_router)
app.include_router(common_router)
app.include_router(resume_router)
app.include_router(user_resume_router)
app.include_router(router_user)
app.include_router(router_lego)
app.include_router(router_template)
app.include_router(upload_router)
app.include_router(integral_router)
app.include_router(pdf_router)
app.include_router(lego_pdf_router)

# 挂载静态文件（上传的文件）
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


_ALLOWED_LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}


def _is_local_host(host: str) -> bool:
    if not host:
        return False
    if host in _ALLOWED_LOCAL_HOSTS:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _is_upload_path_traversal(raw_path: bytes) -> bool:
    path = raw_path.decode("utf-8", "ignore")
    lowered = path.lower()
    is_upload_api = path.startswith("/huajian/upload/file/") or path.startswith(
        "/huajian/upload/filesUpload/"
    )
    if not is_upload_api:
        return False
    return "/../" in path or path.endswith("/..") or "%2e%2e" in lowered


def _generate_disabled_password_hash() -> str:
    # 个人本地模式不依赖账号密码登录，使用随机字符串避免可猜测默认密码。
    random_secret = secrets.token_urlsafe(32)
    return _bcrypt.hashpw(random_secret.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def _rotate_weak_password_if_needed(user) -> bool:
    try:
        if _bcrypt.checkpw(b"admin123", user.password_hash.encode("utf-8")):
            user.password_hash = _generate_disabled_password_hash()
            return True
    except ValueError:
        # 密码哈希格式异常时也进行旋转，避免保留可用口令。
        user.password_hash = _generate_disabled_password_hash()
        return True
    return False


def _ensure_local_default_user():
    from database import SessionLocal
    from models.user import User

    db = SessionLocal()
    try:
        default_user = db.query(User).filter(User.email == DEFAULT_LOCAL_EMAIL).first()
        if not default_user:
            default_user = User(
                name="本地用户",
                email=DEFAULT_LOCAL_EMAIL,
                password_hash=_generate_disabled_password_hash(),
                is_admin=False,
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            print(f"✅ 本地默认用户已创建: {DEFAULT_LOCAL_EMAIL}")
        else:
            updated = _rotate_weak_password_if_needed(default_user)
            if updated:
                db.commit()
                print(f"✅ 默认用户弱密码已轮换: {DEFAULT_LOCAL_EMAIL}")
            else:
                print(f"✅ 本地默认用户已存在: {DEFAULT_LOCAL_EMAIL}")

    finally:
        db.close()


@app.middleware("http")
async def local_only_guard(request: Request, call_next):
    if _is_upload_path_traversal(request.scope.get("raw_path", b"")):
        return api_response(data=None, status=400, message="非法上传路径", http_status=400)

    if not LOCAL_ONLY:
        return await call_next(request)

    client_host = request.client.host if request.client else ""
    if _is_local_host(client_host):
        return await call_next(request)

    return api_response(data=None, status=403, message="仅允许本机访问", http_status=403)


@app.on_event("startup")
def startup():
    """启动时初始化数据库 + 自动创建默认用户"""
    init_db()
    _ensure_local_default_user()

    print("✅ 数据库初始化完成")
    print("✅ 本地简历后端启动成功")
    print("📖 API 文档: http://localhost:8000/docs")


@app.get("/huajian/auth/autoLogin")
def auto_login():
    """免登录端点 — 直接返回默认用户的 token 和信息"""
    if not ALLOW_AUTO_LOGIN:
        return api_response(data=None, status=403, message="自动登录已关闭")

    from database import SessionLocal
    from models.user import User
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == DEFAULT_LOCAL_EMAIL).first()
        if not user:
            return api_response(data=None, status=500, message="默认用户不存在")

        token = create_token(user.email)
        return api_response(data={
            "token": token,
            "userInfo": user.to_user_info(),
        })
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "猫步简历后端 API 运行中", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
