import json
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.user import generate_uuid, utcnow


class LegoCategory(Base):
    """积木设计器分类"""
    __tablename__ = "lego_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "name": self.name,
            "sortOrder": self.sort_order,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
        }


class LegoTemplate(Base):
    """积木设计器模板"""
    __tablename__ = "lego_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    category_id: Mapped[str] = mapped_column(String(36), default="")
    json_data: Mapped[str] = mapped_column(Text, default="{}")
    preview_img: Mapped[str] = mapped_column(Text, default="")
    user_email: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[int] = mapped_column(Integer, default=1)  # 0:待审核 1:通过
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    def to_dict(self) -> dict:
        title = self.name or "未命名模板"
        return {
            "_id": self.id,
            "name": self.name,
            "title": title,
            "categoryId": self.category_id,
            "category": self.category_id,
            "previewImg": self.preview_img,
            "previewUrl": self.preview_img,
            "email": self.user_email,
            "status": self.status,
            "useCount": self.use_count,
            "views": self.use_count,
            "how_much": 0,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
        }

    def to_detail_dict(self) -> dict:
        base = self.to_dict()
        try:
            base["json"] = json.loads(self.json_data) if self.json_data else {}
        except (json.JSONDecodeError, TypeError):
            base["json"] = {}
        base["lego_json"] = base["json"]
        return base


class LegoUserResume(Base):
    """用户积木作品"""
    __tablename__ = "lego_user_resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), default="")
    json_data: Mapped[str] = mapped_column(Text, default="{}")
    preview_img: Mapped[str] = mapped_column(Text, default="")
    template_id: Mapped[str] = mapped_column(String(36), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self) -> dict:
        updated_at = self.updated_at.isoformat() if self.updated_at else ""
        title = self.name or "未命名作品"
        return {
            "_id": self.id,
            "id": self.id,
            "email": self.user_email,
            "name": self.name,
            "title": title,
            "previewImg": self.preview_img,
            "previewUrl": self.preview_img,
            "templateId": self.template_id,
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
        base["lego_json"] = base["json"]
        return base
