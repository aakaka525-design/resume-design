import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from models.user_resume import UserResume
from utils import api_response

router = APIRouter(prefix="/huajian/userresume", tags=["用户简历"])


def _page_info(page: int, limit: int, total: int) -> dict:
    return {
        "count": total,
        "currentPage": page,
        "pageSize": limit,
    }


def _resolve_resume_json(data: dict) -> dict:
    for key in ("json", "templateJson", "template_json"):
        value = data.get(key)
        if isinstance(value, dict):
            return value

    # 兼容旧版设计器：直接把整份简历 JSON 作为请求体
    if isinstance(data, dict) and any(k in data for k in ("TITLE", "COMPONENTS", "GLOBAL_STYLE")):
        return data

    return {}


@router.post("/template")
def save_user_resume(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存用户简历"""
    resume_id = data.get("_id", "") or data.get("id", "") or data.get("resumeId", "")
    template_id = data.get("templateId", "") or data.get("template_id", "") or data.get("ID", "")
    resume_json = _resolve_resume_json(data)
    draft_json_data = data.get("draftJson")
    if draft_json_data is None:
        draft_json_data = data.get("draft_json")
    resume_name = data.get("name", "") or data.get("TITLE", "")
    preview_img = data.get("previewImg", "") or data.get("previewUrl", "") or data.get("template_cover", "")

    if not resume_id and template_id:
        existing = db.query(UserResume).filter(
            UserResume.template_id == template_id,
            UserResume.user_email == user.email,
        ).first()
        if existing:
            resume_id = existing.id

    if resume_id:
        # 更新
        resume = db.query(UserResume).filter(
            UserResume.id == resume_id,
            UserResume.user_email == user.email,
        ).first()
        if not resume:
            return api_response(data=None, status=404, message="简历不存在或无权限")

        resume.json_data = json.dumps(resume_json, ensure_ascii=False)
        resume.name = resume_name or resume.name
        if preview_img:
            resume.preview_img = preview_img
        if draft_json_data is not None:
            resume.draft_json = json.dumps(draft_json_data, ensure_ascii=False) if draft_json_data else ""
            resume.is_draft = bool(draft_json_data)
        db.commit()
        return api_response(data=resume.to_dict())

    # 新增
    resume = UserResume(
        user_email=user.email,
        template_id=template_id,
        name=resume_name,
        json_data=json.dumps(resume_json, ensure_ascii=False),
        draft_json=json.dumps(draft_json_data, ensure_ascii=False) if draft_json_data else "",
        is_draft=bool(draft_json_data),
        preview_img=preview_img,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return api_response(data=resume.to_dict())


@router.get("/templateList")
def get_user_resume_list(
    page: int = 1,
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """查询用户简历列表"""
    query = db.query(UserResume).filter(UserResume.user_email == user.email)
    total = query.count()
    resumes = query.order_by(UserResume.updated_at.desc()) \
        .offset((page - 1) * limit).limit(limit).all()
    return api_response(data={
        "list": [r.to_dict() for r in resumes],
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router.delete("/deleteResume/{resume_id}")
def delete_user_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户删除简历"""
    resume = db.query(UserResume).filter(
        UserResume.id == resume_id, UserResume.user_email == user.email
    ).first()
    if not resume:
        return api_response(data=None, status=404, message="简历不存在")
    db.delete(resume)
    db.commit()
    return api_response(data=True)


@router.post("/publishOnline")
def publish_online_resume(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发布为在线简历"""
    resume_id = data.get("id", "") or data.get("_id", "")
    resume = db.query(UserResume).filter(
        UserResume.id == resume_id,
        UserResume.user_email == user.email,
    ).first()
    if not resume:
        return api_response(data=None, status=404, message="简历不存在")
    resume.is_online = True
    db.commit()
    return api_response(data={"id": resume.id})


@router.put("/updateOnlineResume")
def update_online_resume(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新在线简历设置"""
    resume_id = data.get("id", "") or data.get("_id", "")
    resume = db.query(UserResume).filter(
        UserResume.id == resume_id,
        UserResume.user_email == user.email,
    ).first()
    if not resume:
        return api_response(data=None, status=404, message="简历不存在")
    if "onlineSettings" in data:
        resume.online_settings = json.dumps(data["onlineSettings"], ensure_ascii=False)
    db.commit()
    return api_response(data=True)
