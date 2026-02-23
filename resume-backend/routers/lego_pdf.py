"""积木导出路由（最小可用实现）。"""
from fastapi import APIRouter
from fastapi.responses import Response


router = APIRouter(prefix="/huajian/legoPdf", tags=["积木 PDF/PNG 导出"])


@router.post("/getPdf")
def get_lego_pdf():
    """导出积木 PDF — 返回最小合法 PDF。"""
    minimal_pdf = (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n206\n%%EOF"
    )
    return Response(content=minimal_pdf, media_type="application/pdf")


@router.post("/getPNG")
def get_lego_png():
    """导出积木 PNG — 返回 1x1 透明像素。"""
    minimal_png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00"
        b"\x01\x00\x00\x05\x00\x01\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return Response(content=minimal_png, media_type="image/png")
