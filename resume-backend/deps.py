from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
import bcrypt as _bcrypt
import jwt
import secrets
from datetime import datetime, timedelta, timezone

from config import ALGORITHM, APP_MODE, DEFAULT_LOCAL_EMAIL, SECRET_KEY
from database import get_db
from models.user import User


def create_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _create_local_default_user(db: Session) -> User:
    random_secret = secrets.token_urlsafe(32)
    user = User(
        name="本地用户",
        email=DEFAULT_LOCAL_EMAIL,
        password_hash=_bcrypt.hashpw(random_secret.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8"),
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """从 Authorization header 解析 JWT token，获取当前用户。"""
    token = request.headers.get("Authorization", "").strip()

    if token:
        # 前端可能带 Bearer 前缀也可能不带
        if token.startswith("Bearer "):
            token = token[7:]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("email", "")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return user
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            if APP_MODE != "local":
                raise HTTPException(status_code=401, detail="Token 无效或已过期")

    if APP_MODE == "local":
        default_user = db.query(User).filter(User.email == DEFAULT_LOCAL_EMAIL).first()
        if default_user:
            return default_user
        return _create_local_default_user(db)

    raise HTTPException(status_code=401, detail="未登录")


def get_optional_user(request: Request, db: Session = Depends(get_db)):
    """可选的用户认证，不强制要求登录"""
    token = request.headers.get("Authorization", "").strip()
    if not token:
        return None
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None
