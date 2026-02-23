import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from deps import get_current_user
from models.lego import LegoTemplate, LegoUserResume
from models.user import User
from utils import api_response

router_lego = APIRouter(prefix="/huajian/lego", tags=["积木作品"])
router_template = APIRouter(prefix="/huajian/legoTemplate", tags=["积木模板"])


def _page_info(page: int, limit: int, total: int) -> dict:
    return {
        "count": total,
        "currentPage": page,
        "pageSize": limit,
    }


def _resolve_lego_json(data: dict) -> dict:
    for key in ("json", "lego_json", "legoJson"):
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return {}


@router_lego.post("/legoUserResume")
def save_lego_user_resume(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume_id = data.get("_id", "") or data.get("id", "")
    lego_json = _resolve_lego_json(data)
    title = data.get("name", "") or data.get("title", "")
    preview_img = data.get("previewImg", "") or data.get("previewUrl", "")
    template_id = data.get("templateId", "")

    if resume_id:
        resume = db.query(LegoUserResume).filter(
            LegoUserResume.id == resume_id,
            LegoUserResume.user_email == user.email,
        ).first()
        if not resume:
            return api_response(data=None, status=404, message="作品不存在或无权限")

        resume.json_data = json.dumps(lego_json, ensure_ascii=False)
        resume.name = title or resume.name
        if preview_img:
            resume.preview_img = preview_img
        if template_id:
            resume.template_id = template_id
        db.commit()
        return api_response(data=resume.to_dict())

    resume = LegoUserResume(
        user_email=user.email,
        name=title,
        json_data=json.dumps(lego_json, ensure_ascii=False),
        preview_img=preview_img,
        template_id=template_id,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return api_response(data=resume.to_dict())


@router_lego.get("/legoUserResumeList")
def get_lego_user_resume_list(
    page: int = 1,
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(LegoUserResume).filter(LegoUserResume.user_email == user.email)
    total = query.count()
    resumes = query.order_by(LegoUserResume.updated_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return api_response(data={
        "list": [r.to_dict() for r in resumes],
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router_lego.get("/legoUserResumeById/{resume_id}")
def get_lego_user_resume_by_id(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(LegoUserResume).filter(
        LegoUserResume.id == resume_id,
        LegoUserResume.user_email == user.email,
    ).first()
    if not resume:
        return api_response(data=None, status=404, message="作品不存在")
    return api_response(data=resume.to_detail_dict())


@router_lego.delete("/deleteLegoUserResume/{resume_id}")
def delete_lego_user_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(LegoUserResume).filter(
        LegoUserResume.id == resume_id,
        LegoUserResume.user_email == user.email,
    ).first()
    if resume:
        db.delete(resume)
        db.commit()
    return api_response(data=True)


@router_template.get("/legoUserTemplateByIdAndJsonId")
def get_lego_user_template_detail(
    id: str = "",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    template = db.query(LegoTemplate).filter(
        LegoTemplate.id == id,
        LegoTemplate.user_email == user.email,
    ).first()
    if not template:
        return api_response(data=None, status=404, message="模板不存在")
    return api_response(data=template.to_detail_dict())


@router_template.get("/legoTemplateInfoById/{template_id}")
def get_lego_template_by_id(template_id: str, db: Session = Depends(get_db)):
    template = db.query(LegoTemplate).filter(LegoTemplate.id == template_id).first()
    if not template:
        return api_response(data=None, status=404, message="模板不存在")
    return api_response(data=template.to_detail_dict())
