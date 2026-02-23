from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.template import Template
from utils import api_response

router = APIRouter(prefix="/huajian/resume", tags=["简历模板"])


@router.get("/template/{template_id}")
def get_template_info(template_id: str, db: Session = Depends(get_db)):
    """读取模板详情。"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return api_response(data=None, status=404, message="模板不存在")
    detail = template.to_detail_dict()
    return api_response(data=detail.get("template_json", {}))


@router.get("/templateReset/{template_id}")
def get_reset_template_info(template_id: str, db: Session = Depends(get_db)):
    """读取模板原始 JSON。"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return api_response(data=None, status=404, message="模板不存在")
    detail = template.to_detail_dict()
    return api_response(data=detail.get("template_json", {}))
