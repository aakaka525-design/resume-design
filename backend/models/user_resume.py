import json
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.user import generate_uuid, utcnow


class UserResume(Base):
    """用户简历（旧版在线制作设计器）"""
    __tablename__ = "user_resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    template_id: Mapped[str] = mapped_column(String(36), default="")
    name: Mapped[str] = mapped_column(String(200), default="")
    json_data: Mapped[str] = mapped_column(Text, default="{}")
    draft_json: Mapped[str] = mapped_column(Text, default="")
    is_draft: Mapped[bool] = mapped_column(Boolean, default=False)
    preview_img: Mapped[str] = mapped_column(Text, default="")
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否发布为在线简历
    online_settings: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        updated_at = self.updated_at.isoformat() if self.updated_at else ""
        return {
            "_id": self.id,
            "id": self.id,
            "email": self.user_email,
            "templateId": self.template_id,
            "template_id": self.template_id,
            "name": self.name,
            "previewImg": self.preview_img,
            "previewUrl": self.preview_img,
            "template_cover": self.preview_img,
            "template_title": self.name,
            "isDraft": self.is_draft,
            "isOnline": self.is_online,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
            "updatedAt": updated_at,
            "updateDate": updated_at,
        }

    def to_detail_dict(self) -> dict:
        base = self.to_dict()
        try:
            base["json"] = json.loads(self.json_data) if self.json_data else {}
        except (json.JSONDecodeError, TypeError):
            base["json"] = {}
        try:
            base["draftJson"] = json.loads(self.draft_json) if self.draft_json else None
        except (json.JSONDecodeError, TypeError):
            base["draftJson"] = None
        base["template_json"] = base["draftJson"] or base["json"] or {}
        base["templateJson"] = base["template_json"]
        return base


class CreateUserTemplate(Base):
    """用户创建的简历（新版在线制作/贡献模板）"""
    __tablename__ = "create_user_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    template_id: Mapped[str] = mapped_column(String(36), default="")
    name: Mapped[str] = mapped_column(String(200), default="")
    json_data: Mapped[str] = mapped_column(Text, default="{}")
    draft_json: Mapped[str] = mapped_column(Text, default="")
    is_draft: Mapped[bool] = mapped_column(Boolean, default=False)
    preview_img: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        updated_at = self.updated_at.isoformat() if self.updated_at else ""
        return {
            "_id": self.id,
            "id": self.id,
            "email": self.user_email,
            "templateId": self.template_id,
            "template_id": self.template_id,
            "name": self.name,
            "template_title": self.name,
            "previewImg": self.preview_img,
            "previewUrl": self.preview_img,
            "template_cover": self.preview_img,
            "isDraft": self.is_draft,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
            "updatedAt": updated_at,
            "updateDate": updated_at,
        }

    def to_detail_dict(self) -> dict:
        base = self.to_dict()
        try:
            base["json"] = json.loads(self.json_data) if self.json_data else {}
        except (json.JSONDecodeError, TypeError):
            base["json"] = {}
        try:
            base["draftJson"] = json.loads(self.draft_json) if self.draft_json else None
        except (json.JSONDecodeError, TypeError):
            base["draftJson"] = None
        base["template_json"] = base["draftJson"] or base["json"] or {}
        base["templateJson"] = base["template_json"]
        return base
