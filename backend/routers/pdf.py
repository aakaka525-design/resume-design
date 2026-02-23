"""PDF/PNG 导出接口。

个人本地模式下，PDF 采用 Chromium 渲染以获得更高的版式一致性。
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from utils import api_response

router = APIRouter(prefix="/huajian/pdf", tags=["PDF/PNG 导出"])

_ROOT_DIR = Path(__file__).resolve().parents[2]
_FRONTEND_DIR = _ROOT_DIR / "frontend"
_RENDER_SCRIPT = _FRONTEND_DIR / "scripts" / "render_html_pdf.mjs"


class PdfRenderPayload(BaseModel):
    html: str = Field(min_length=1, max_length=8_000_000)
    title: str = Field(default="我的简历", max_length=120)


def _safe_filename(name: str) -> str:
    normalized = "".join(ch for ch in name if ch not in r'\/:*?"<>|').strip()
    return normalized or "我的简历"


def _cleanup_files(*paths: str) -> None:
    for file_path in paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            # 清理失败不影响主流程
            pass


def _run_pdf_render(html: str) -> tuple[str, str, int]:
    if not _RENDER_SCRIPT.is_file():
        raise HTTPException(
            status_code=503,
            detail=f"PDF 渲染脚本缺失: {_RENDER_SCRIPT}",
        )
    if not _FRONTEND_DIR.is_dir():
        raise HTTPException(
            status_code=503,
            detail=f"前端目录缺失: {_FRONTEND_DIR}",
        )

    html_fd, html_path = tempfile.mkstemp(prefix="resume-export-", suffix=".html")
    pdf_fd, pdf_path = tempfile.mkstemp(prefix="resume-export-", suffix=".pdf")
    os.close(html_fd)
    os.close(pdf_fd)

    with open(html_path, "w", encoding="utf-8") as fp:
        fp.write(html)

    try:
        completed = subprocess.run(
            ["node", str(_RENDER_SCRIPT), html_path, pdf_path],
            cwd=str(_FRONTEND_DIR),
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        _cleanup_files(html_path, pdf_path)
        raise HTTPException(status_code=504, detail="PDF 渲染超时，请重试") from exc

    if completed.returncode != 0:
        stderr = (completed.stderr or "").strip()
        stdout = (completed.stdout or "").strip()
        _cleanup_files(html_path, pdf_path)
        raise HTTPException(
            status_code=500,
            detail=f"PDF 渲染失败: {stderr or stdout or 'unknown error'}",
        )

    page_count = 1
    stdout = (completed.stdout or "").strip()
    if stdout:
        last_line = stdout.splitlines()[-1]
        try:
            payload = json.loads(last_line)
            raw_count = int(payload.get("pageCount", 1))
            page_count = raw_count if raw_count > 0 else 1
        except (ValueError, TypeError, json.JSONDecodeError):
            page_count = 1

    if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) <= 0:
        _cleanup_files(html_path, pdf_path)
        raise HTTPException(status_code=500, detail="PDF 文件生成失败")

    return html_path, pdf_path, page_count


def _render_pdf_response(payload: PdfRenderPayload):
    html_path, pdf_path, page_count = _run_pdf_render(payload.html)
    filename = f"{_safe_filename(payload.title)}.pdf"
    cleanup_task = BackgroundTask(_cleanup_files, html_path, pdf_path)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=filename,
        headers={"X-Page-Count": str(page_count)},
        background=cleanup_task,
    )


@router.post("/getPdf")
def get_pdf(payload: PdfRenderPayload):
    """高保真 PDF 导出（Chromium）"""
    return _render_pdf_response(payload)


@router.post("/resumePreview")
def resume_preview(payload: PdfRenderPayload):
    """高保真 PDF 预览（与导出共用渲染管线）"""
    return _render_pdf_response(payload)


@router.get("/getPNG")
def get_png():
    """PNG 导出目前仍由前端 html2canvas 处理"""
    return api_response(data=None, message="请使用客户端导出")


@router.get("/addMakeResumeCount")
def add_make_resume_count():
    """增加导出计数"""
    return api_response(data=True)
