import json
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.user import generate_uuid, utcnow

DEFAULT_TEMPLATE_JSON = {
    "id": "",
    "version": "1.0.0",
    "componentsTree": [],
    "i18n": {},
    "constants": {},
    "props": {"pageName": "BasePage", "title": "猫步简历"},
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
    "config": {"title": "猫步简历", "layout": {"children": []}},
    "meta": {},
    "dataSource": {},
}


def _safe_template_json(raw_json: str) -> dict:
    try:
        loaded = json.loads(raw_json) if raw_json else {}
    except (json.JSONDecodeError, TypeError):
        return {}

    if not isinstance(loaded, dict):
        return {}

    # 兼容历史字段命名
    for key in ("template_json", "templateJson", "json"):
        value = loaded.get(key)
        if isinstance(value, dict):
            return value

    return loaded


def _normalize_template_json(template_json: dict, template_title: str) -> dict:
    normalized = json.loads(json.dumps(DEFAULT_TEMPLATE_JSON, ensure_ascii=False))
    if isinstance(template_json, dict):
        normalized.update(template_json)

    if not isinstance(normalized.get("componentsTree"), list):
        normalized["componentsTree"] = []
    if not isinstance(normalized.get("i18n"), dict):
        normalized["i18n"] = {}
    if not isinstance(normalized.get("constants"), dict):
        normalized["constants"] = {}
    if not isinstance(normalized.get("meta"), dict):
        normalized["meta"] = {}
    if not isinstance(normalized.get("dataSource"), dict):
        normalized["dataSource"] = {}
    if not isinstance(normalized.get("customCss"), list):
        normalized["customCss"] = []

    props = normalized.get("props") if isinstance(normalized.get("props"), dict) else {}
    props["pageName"] = props.get("pageName") or "BasePage"
    props["title"] = props.get("title") or template_title or "猫步简历"
    normalized["props"] = props

    css = normalized.get("css") if isinstance(normalized.get("css"), dict) else {}
    css_defaults = DEFAULT_TEMPLATE_JSON["css"]
    for key, value in css_defaults.items():
        css[key] = css.get(key, value)
    normalized["css"] = css

    config = normalized.get("config") if isinstance(normalized.get("config"), dict) else {}
    config["title"] = config.get("title") or template_title or props["title"] or "猫步简历"
    if not isinstance(config.get("layout"), dict):
        config["layout"] = {"children": []}
    normalized["config"] = config

    return normalized


class TemplateCategory(Base):
    """模板分类"""
    __tablename__ = "template_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "name": self.name,
            "label": self.name,
            "value": self.name,
            "category_label": self.name,
            "category_value": self.name,
            "sortOrder": self.sort_order,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
        }


class Template(Base):
    """简历模板（在线制作设计器的模板列表）"""
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(200), default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    profile_photo: Mapped[str] = mapped_column(Text, default="")  # 头像/缩略图
    preview_img: Mapped[str] = mapped_column(Text, default="")  # 预览图
    json_data: Mapped[str] = mapped_column(Text, default="{}")  # 完整 JSON 数据
    user_email: Mapped[str] = mapped_column(String(255), default="")
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[int] = mapped_column(Integer, default=1)  # 0:待审核 1:已通过 2:已拒绝
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        template_title = self.title or self.name or "未命名简历"
        preview_url = self.preview_img or ""
        views = int(self.use_count or 0)
        created_at = self.created_at.isoformat() if self.created_at else ""
        updated_at = self.updated_at.isoformat() if self.updated_at else ""
        return {
            "_id": self.id,
            "id": self.id,
            "ID": self.id,
            "name": self.name,
            "NAME": self.name,
            "TITLE": template_title,
            "title": template_title,
            "template_title": template_title,
            "category": self.category,
            "template_style": self.category,
            "template_use": "",
            "template_industry": "",
            "previewImg": self.preview_img,
            "previewUrl": preview_url,
            "template_cover": preview_url,
            "profilePhoto": self.profile_photo,
            "isPublic": self.is_public,
            "status": self.status,
            "useCount": self.use_count,
            "VIEWS": views,
            "template_views": views,
            "LIKES": 0,
            "commentCount": 0,
            "userInfo": {
                "name": "",
                "userId": "",
                "avatar": self.profile_photo or "",
            },
            "email": self.user_email,
            "createdAt": created_at,
            "updatedAt": updated_at,
            "updateDate": updated_at,
        }

    def to_detail_dict(self) -> dict:
        base = self.to_dict()
        template_json = _normalize_template_json(
            _safe_template_json(self.json_data),
            base.get("template_title", ""),
        )
        base["json"] = template_json
        base["template_json"] = template_json
        base["templateJson"] = template_json
        return base
