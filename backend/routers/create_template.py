import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.user import User
from models.user_resume import CreateUserTemplate
from utils import api_response

router_user = APIRouter(prefix="/huajian/createUserTemplate", tags=["用户简历草稿"])


def _page_info(page: int, limit: int, total: int) -> dict:
    return {
        "count": total,
        "currentPage": page,
        "pageSize": limit,
    }


@router_user.post("/saveDraft")
def save_draft(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume_id = data.get("_id", "") or data.get("id", "")
    template_id = data.get("templateId", "")
    template_json = data.get("templateJson") or data.get("template_json") or data.get("json") or {}
    draft_json = data.get("draftJson")
    if draft_json is None:
        draft_json = template_json

    resume_name = data.get("name", "")
    if not resume_name and isinstance(template_json, dict):
        resume_name = template_json.get("config", {}).get("title", "")

    if resume_id:
        resume = db.query(CreateUserTemplate).filter(
            CreateUserTemplate.id == resume_id,
            CreateUserTemplate.user_email == user.email,
        ).first()
        if not resume:
            return api_response(data=None, status=404, message="简历不存在或无权限")

        resume.json_data = json.dumps(template_json, ensure_ascii=False)
        resume.draft_json = json.dumps(draft_json, ensure_ascii=False) if draft_json else ""
        resume.name = resume_name or resume.name
        if "previewImg" in data:
            resume.preview_img = data["previewImg"]
        resume.is_draft = True
        db.commit()
        return api_response(data=resume.to_detail_dict())

    resume = CreateUserTemplate(
        user_email=user.email,
        template_id=template_id,
        name=resume_name,
        json_data=json.dumps(template_json, ensure_ascii=False),
        draft_json=json.dumps(draft_json, ensure_ascii=False) if draft_json else "",
        preview_img=data.get("previewImg", ""),
        is_draft=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return api_response(data=resume.to_detail_dict())


@router_user.get("/getUsertemplate/{template_id}")
def get_user_template(
    template_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(CreateUserTemplate).filter(
        CreateUserTemplate.id == template_id,
        CreateUserTemplate.user_email == user.email,
    ).first()
    if not resume:
        return api_response(data=None, status=404, message="简历不存在")
    return api_response(data=resume.to_detail_dict())


@router_user.get("/getMyResumeList")
def get_my_resume_list(
    page: int = 1,
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(CreateUserTemplate).filter(CreateUserTemplate.user_email == user.email)
    total = query.count()
    resumes = query.order_by(CreateUserTemplate.updated_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return api_response(data={
        "list": [r.to_detail_dict() for r in resumes],
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router_user.delete("/deleteUserResume/{resume_id}")
def delete_user_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(CreateUserTemplate).filter(
        CreateUserTemplate.id == resume_id,
        CreateUserTemplate.user_email == user.email,
    ).first()
    if resume:
        db.delete(resume)
        db.commit()
    return api_response(data=True)
