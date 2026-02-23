import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.getenv("SECRET_KEY", "resume-design-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30


def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


APP_MODE = os.getenv("APP_MODE", "local").strip().lower()
LOCAL_ONLY = _env_bool("LOCAL_ONLY", "true")
ALLOW_AUTO_LOGIN = _env_bool("ALLOW_AUTO_LOGIN", "true")
DEFAULT_LOCAL_EMAIL = os.getenv("DEFAULT_LOCAL_EMAIL", "local@resume").strip().lower()

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'resume.db')}"

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
