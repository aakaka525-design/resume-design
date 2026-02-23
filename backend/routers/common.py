from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.lego import LegoCategory, LegoTemplate
from models.template import Template, TemplateCategory
from utils import api_response

router = APIRouter(prefix="/huajian/common", tags=["公共接口"])


def _page_info(page: int, limit: int, total: int) -> dict:
    return {
        "count": total,
        "currentPage": page,
        "pageSize": limit,
    }


def _template_category_payload(db: Session) -> list[dict]:
    categories = db.query(TemplateCategory).order_by(TemplateCategory.sort_order).all()
    if categories:
        return [c.to_dict() for c in categories]

    rows = (
        db.query(Template.category)
        .filter(Template.category.is_not(None), Template.category != "")
        .distinct()
        .all()
    )
    fallback: list[dict] = []
    for index, (name,) in enumerate(rows):
        fallback.append({
            "_id": f"fallback-{index}",
            "name": name,
            "label": name,
            "value": name,
            "category_label": name,
            "category_value": name,
            "sortOrder": index,
            "createdAt": "",
        })
    return fallback


@router.get("/getTemplateList")
def get_template_list(
    page: int = 1,
    limit: int = 10,
    category: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(Template).filter(Template.status == 1, Template.is_public.is_(True))
    if category:
        query = query.filter(Template.category == category)
    total = query.count()
    templates = query.order_by(Template.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return api_response(data={
        "list": [t.to_dict() for t in templates],
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router.get("/templateList")
def get_common_template_list(
    page: int = 1,
    limit: int = 10,
    templateStatus: int = 1,
    templateStyle: str = "",
    templateUse: str = "",
    templateIndustry: str = "",
    templatePost: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(Template)
    if templateStatus in {0, 1}:
        query = query.filter(Template.status == templateStatus)
    if templateStyle:
        query = query.filter(Template.category == templateStyle)
    # 最小本地版不区分用途/行业/岗位，参数保留仅为兼容前端调用。
    _ = templateUse, templateIndustry, templatePost

    total = query.count()
    templates = query.order_by(Template.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return api_response(data={
        "list": [t.to_dict() for t in templates],
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router.get("/template/{template_id}")
def get_template_by_id(template_id: str, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        return api_response(data=None, status=404, message="模板不存在")
    return api_response(data=template.to_detail_dict())


@router.get("/getTemplateCategoryList")
def get_template_category_list(db: Session = Depends(get_db)):
    return api_response(data=_template_category_payload(db))


@router.get("/getCategoryList")
def get_category_list(db: Session = Depends(get_db)):
    return api_response(data=_template_category_payload(db))


@router.get("/getLegoCategoryList")
def get_lego_category_list(db: Session = Depends(get_db)):
    categories = db.query(LegoCategory).order_by(LegoCategory.sort_order).all()
    return api_response(data=[c.to_dict() for c in categories])


@router.get("/getLegoTemplateListByCategory")
def get_lego_template_by_category(
    category: str = "",
    categoryId: str = "",
    page: int = 1,
    limit: int = 10,
    sort: str = "",
    db: Session = Depends(get_db),
):
    query = db.query(LegoTemplate).filter(LegoTemplate.status == 1)

    category_value = categoryId or category
    if category_value:
        category_obj = db.query(LegoCategory).filter(LegoCategory.name == category_value).first()
        if category_obj:
            query = query.filter(LegoTemplate.category_id == category_obj.id)
        else:
            query = query.filter(LegoTemplate.category_id == category_value)

    if sort == "time":
        query = query.order_by(LegoTemplate.created_at.desc())
    else:
        query = query.order_by(LegoTemplate.created_at.desc())

    total = query.count()
    templates = query.offset((page - 1) * limit).limit(limit).all()

    # 把分类名称映射回前端展示字段
    category_map = {
        item.id: item.name
        for item in db.query(LegoCategory).all()
    }
    result = []
    for template in templates:
        item = template.to_dict()
        item["category"] = category_map.get(template.category_id, template.category_id)
        result.append(item)

    return api_response(data={
        "list": result,
        "total": total,
        "page": _page_info(page, limit, total),
        "currentPage": page,
        "pageSize": limit,
        "limit": limit,
    })


@router.get("/addWebsiteViews")
def add_website_views():
    return api_response(data=True)


@router.get("/getWebsiteConfig")
def get_website_config():
    return api_response(data={
        "all_free": True,
        "open_comment": False,
        "website_title": "猫步简历（本地版）",
    })


@router.get("/getIndexMenuList")
def get_index_menu_list():
    return api_response(data=[
        {"_id": "1", "name": "首页", "path": "/", "sort": 0, "show": True, "status": 1, "children": []},
        {"_id": "2", "name": "简历模板", "path": "/resume", "sort": 1, "show": True, "status": 1, "children": []},
        {"_id": "3", "name": "积木模板", "path": "/legoTemplateList", "sort": 2, "show": True, "status": 1, "children": []},
    ])
