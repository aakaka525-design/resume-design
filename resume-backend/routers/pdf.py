"""PDF/PNG 导出最小接口。

实际导出由前端客户端完成，后端仅提供兼容接口与计数。
"""
from fastapi import APIRouter

from utils import api_response

router = APIRouter(prefix="/huajian/pdf", tags=["PDF/PNG 导出"])


@router.post("/getPdf")
def get_pdf():
    """PDF 导出 — 由前端 html2canvas 处理，此端点仅防 404"""
    return api_response(data=None, message="请使用客户端导出")


@router.post("/resumePreview")
def resume_preview():
    """PDF 预览 — 由前端处理"""
    return api_response(data=None, message="请使用客户端导出")


@router.get("/getPNG")
def get_png():
    """PNG 导出 — 由前端 html2canvas 处理"""
    return api_response(data=None, message="请使用客户端导出")


@router.get("/addMakeResumeCount")
def add_make_resume_count():
    """增加导出计数"""
    return api_response(data=True)
