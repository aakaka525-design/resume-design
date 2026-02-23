import os
from pathlib import Path
import re
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from config import UPLOAD_DIR
from deps import get_current_user
from models.user import User
from utils import api_response

router = APIRouter(prefix="/huajian/upload", tags=["文件上传"])
_SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9_/-]+$")


def _resolve_safe_upload_dir(path: str) -> tuple[Path, str]:
    normalized = (path or "").strip().strip("/")
    if not normalized:
        raise HTTPException(status_code=400, detail="非法上传路径")
    if not _SAFE_PATH_RE.fullmatch(normalized):
        raise HTTPException(status_code=400, detail="上传路径仅允许字母数字下划线和斜杠")

    parts = [p for p in normalized.split("/") if p]
    if any(part in {".", ".."} for part in parts):
        raise HTTPException(status_code=400, detail="上传路径包含非法段")
    normalized = "/".join(parts)

    base_dir = Path(UPLOAD_DIR).resolve()
    upload_dir = (base_dir / normalized).resolve()
    try:
        upload_dir.relative_to(base_dir)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="上传路径越界") from exc

    return upload_dir, normalized


@router.post("/filesUpload/{path:path}")
async def files_upload(
    path: str,
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
):
    """文件上传 — 保存到本地 uploads 目录"""
    if not file:
        return api_response(data=None, status=400, message="未上传文件")

    upload_path, safe_path = _resolve_safe_upload_dir(path)
    os.makedirs(upload_path, exist_ok=True)

    # 生成唯一文件名
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = upload_path / filename

    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回访问 URL
    file_url = f"/uploads/{safe_path}/{filename}"
    return api_response(data={
        "url": file_url,
        "name": file.filename,
        "size": len(content),
    })


@router.post("/file/{path:path}")
async def file_upload_compat(
    path: str,
    request: Request,
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
):
    """文件上传（兼容端点）— 匹配前端 /huajian/upload/file/{type} 路径。
    返回 {fileUrl: "..."} 格式，与前端 el-upload 的 response.data.data.fileUrl 契约一致。
    """
    if not file:
        return api_response(data=None, status=400, message="未上传文件")

    upload_path, safe_path = _resolve_safe_upload_dir(path)
    os.makedirs(upload_path, exist_ok=True)

    # 生成唯一文件名
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = upload_path / filename

    # 保存文件
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 返回完整 URL（前端需要绝对路径显示图片）
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/uploads/{safe_path}/{filename}"
    return api_response(data={
        "fileUrl": file_url,
        "url": file_url,
        "name": file.filename,
        "size": len(content),
    })
