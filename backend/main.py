import ipaddress
import json
import os
import secrets
from pathlib import Path

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
_DEFAULT_TEMPLATE_PREVIEW = "/static/img/normal.webp"


def _resolve_seed_file(relative_path: str) -> str | None:
    backend_dir = Path(__file__).resolve().parent
    candidates = [
        backend_dir.parent / "frontend" / relative_path,
        backend_dir.parent / relative_path,
        backend_dir.parent.parent / "resume-design" / "frontend" / relative_path,
    ]
    for path in candidates:
        if path.is_file():
            return str(path)
    return None


_FRONTEND_TEMPLATES_JSON = _resolve_seed_file("public/static/templates.json")
_FRONTEND_FULL_TEMPLATE_SEED_JSON = _resolve_seed_file("ssr-data/resume.templates.json")


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


def _load_template_meta_seed() -> list[dict]:
    fallback = [
        {"id": "local-template-001", "title": "本地默认模板 A"},
        {"id": "local-template-002", "title": "本地默认模板 B"},
        {"id": "local-template-003", "title": "本地默认模板 C"},
    ]
    if not _FRONTEND_TEMPLATES_JSON or not os.path.isfile(_FRONTEND_TEMPLATES_JSON):
        return fallback
    try:
        with open(_FRONTEND_TEMPLATES_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return fallback
        result: list[dict] = []
        seen_ids: set[str] = set()
        for item in data:
            if not isinstance(item, dict):
                continue
            template_id = str(item.get("id", "")).strip()
            title = str(item.get("title", "")).strip()
            if not template_id:
                continue
            if len(template_id) > 36:
                template_id = template_id[:36]
            if template_id in seen_ids:
                continue
            seen_ids.add(template_id)
            result.append(
                {
                    "id": template_id,
                    "title": title or "本地模板",
                }
            )
        return result or fallback
    except Exception:
        return fallback


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_template_id(raw_id) -> str:
    if isinstance(raw_id, dict):
        raw_id = raw_id.get("$oid", "")
    template_id = str(raw_id or "").strip()
    if len(template_id) > 36:
        template_id = template_id[:36]
    return template_id


def _load_template_full_seed() -> list[dict]:
    if not _FRONTEND_FULL_TEMPLATE_SEED_JSON or not os.path.isfile(_FRONTEND_FULL_TEMPLATE_SEED_JSON):
        return []
    try:
        with open(_FRONTEND_FULL_TEMPLATE_SEED_JSON, "r", encoding="utf-8") as f:
            rows = json.load(f)
        if not isinstance(rows, list):
            return []

        result: list[dict] = []
        seen_ids: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            template_id = _normalize_template_id(row.get("_id", row.get("id", "")))
            if not template_id or template_id in seen_ids:
                continue
            seen_ids.add(template_id)

            title = str(row.get("template_title", row.get("title", ""))).strip() or "本地模板"
            template_json = row.get("template_json")
            if not isinstance(template_json, dict):
                template_json = _build_default_template_json(title)

            category = str(row.get("template_style", "")).strip() or "默认"
            preview_img = str(row.get("template_cover", "")).strip() or _DEFAULT_TEMPLATE_PREVIEW
            status = _safe_int(row.get("template_status", 1), 1)
            use_count = _safe_int(row.get("template_views", 0), 0)
            result.append({
                "id": template_id,
                "title": title,
                "category": category,
                "preview_img": preview_img,
                "template_json": template_json,
                "status": status if status in {0, 1, 2} else 1,
                "use_count": max(0, use_count),
            })
        return result
    except Exception:
        return []


def _template_has_components(json_data: str) -> bool:
    try:
        payload = json.loads(json_data) if json_data else {}
    except (TypeError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict):
        return False
    components = payload.get("componentsTree")
    return isinstance(components, list) and len(components) > 0


def _ensure_category_rows(db, category_names: list[str]) -> int:
    from models.template import TemplateCategory

    existing_rows = db.query(TemplateCategory).order_by(TemplateCategory.sort_order).all()
    existing_names = {row.name for row in existing_rows}
    sort_order = len(existing_rows)
    created = 0
    for name in category_names:
        normalized = name.strip()
        if not normalized or normalized in existing_names:
            continue
        db.add(TemplateCategory(name=normalized, sort_order=sort_order))
        sort_order += 1
        created += 1
        existing_names.add(normalized)
    return created


def _build_default_template_json(template_title: str) -> dict:
    return {
        "id": "",
        "version": "1.0.0",
        "componentsTree": [],
        "i18n": {},
        "constants": {},
        "props": {"pageName": "BasePage", "title": template_title or "猫步简历"},
        "css": {
            "width": 820,
            "height": "100%",
            "background": "#ffffff",
            "opacity": 1,
            "backgroundImage": "",
            "fontFamily": "",
            "themeColor": "",
        },
        "customCss": [],
        "config": {"title": template_title or "猫步简历", "layout": {"children": []}},
        "meta": {},
        "dataSource": {},
    }


def _ensure_default_templates():
    from database import SessionLocal
    from models.template import Template, TemplateCategory

    db = SessionLocal()
    try:
        full_seed = _load_template_full_seed()
        if db.query(Template).count() == 0:
            if full_seed:
                category_names = sorted({item["category"] for item in full_seed if item.get("category")})
                if not category_names:
                    category_names = ["默认"]
                _ensure_category_rows(db, category_names)

                for item in full_seed:
                    db.add(
                        Template(
                            id=item["id"],
                            name=item["title"],
                            title=item["title"],
                            category=item["category"],
                            preview_img=item["preview_img"],
                            json_data=json.dumps(item["template_json"], ensure_ascii=False),
                            is_public=True,
                            status=item["status"],
                            use_count=item["use_count"],
                        )
                    )
                db.commit()
                print(f"✅ 已初始化本地模板数据(完整种子): {len(full_seed)} 条")
                return

            default_category = db.query(TemplateCategory).filter(TemplateCategory.name == "默认").first()
            if not default_category:
                default_category = TemplateCategory(name="默认", sort_order=0)
                db.add(default_category)
                db.flush()

            template_seed = _load_template_meta_seed()
            for idx, item in enumerate(template_seed, start=1):
                title = item["title"]
                template_json = _build_default_template_json(title)
                db.add(
                    Template(
                        id=item["id"],
                        name=title,
                        title=title,
                        category="默认",
                        preview_img=_DEFAULT_TEMPLATE_PREVIEW,
                        json_data=json.dumps(template_json, ensure_ascii=False),
                        is_public=True,
                        status=1,
                        use_count=max(0, len(template_seed) - idx),
                    )
                )
            db.commit()
            print(f"✅ 已初始化本地模板数据(最小种子): {len(template_seed)} 条")
            return

        if not full_seed:
            return

        seed_map = {item["id"]: item for item in full_seed}
        updated = 0
        category_candidates: set[str] = set()
        templates = db.query(Template).all()
        for template in templates:
            seed_item = seed_map.get(template.id)
            if not seed_item:
                continue
            changed = False

            if seed_item["category"]:
                category_candidates.add(seed_item["category"])

            # 占位封面或缺失封面时，回填真实封面地址
            if (not template.preview_img or template.preview_img == _DEFAULT_TEMPLATE_PREVIEW) and seed_item["preview_img"]:
                template.preview_img = seed_item["preview_img"]
                changed = True

            # 占位分类时，回填真实风格分类
            if (not template.category or template.category == "默认") and seed_item["category"]:
                template.category = seed_item["category"]
                changed = True

            # 模板结构为空时，回填完整模板 JSON
            if not _template_has_components(template.json_data):
                template.json_data = json.dumps(seed_item["template_json"], ensure_ascii=False)
                changed = True

            if template.status not in {0, 1, 2}:
                template.status = seed_item["status"]
                changed = True

            if (template.use_count or 0) <= 0 and seed_item["use_count"] > 0:
                template.use_count = seed_item["use_count"]
                changed = True

            if changed:
                updated += 1

        created_categories = _ensure_category_rows(db, sorted(category_candidates))
        if updated or created_categories:
            db.commit()
            print(f"✅ 模板数据已回填: {updated} 条, 新增分类: {created_categories} 条")
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
    _ensure_default_templates()

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
