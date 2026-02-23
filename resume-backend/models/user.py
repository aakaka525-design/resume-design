import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(Text, default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    def to_user_info(self) -> dict:
        """返回前端最小 userInfo 结构。"""
        return {
            "_id": self.id,
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "avatar": self.avatar,
            "photos": {
                "profilePic": {
                    "url": self.avatar or "",
                }
            },
            "auth": {
                "email": {
                    "valid": True
                }
            },
            "isAllFree": True,
            "createdAt": self.created_at.isoformat() if self.created_at else "",
        }
