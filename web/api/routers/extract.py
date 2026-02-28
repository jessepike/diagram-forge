"""POST /extract — file text extraction endpoint."""

from __future__ import annotations

from io import BytesIO

import fitz  # PyMuPDF
from docx import Document
from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter()

_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md"}


def _get_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[1].lower()


@router.post("/extract")
async def extract_text(file: UploadFile) -> dict:
    """Extract text from PDF, DOCX, or Markdown files."""
    ext = _get_extension(file.filename)
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type '{ext}'; allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}")

    data = await file.read()
    if len(data) > _MAX_SIZE:
        raise HTTPException(status_code=422, detail=f"File exceeds 10 MB limit ({len(data)} bytes)")

    try:
        if ext == ".pdf":
            text = _extract_pdf(data)
        elif ext == ".docx":
            text = _extract_docx(data)
        else:
            text = data.decode("utf-8")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Failed to parse {ext} file: {exc}") from exc

    return {
        "text": text,
        "filename": file.filename,
        "char_count": len(text),
    }


def _extract_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def _extract_docx(data: bytes) -> str:
    doc = Document(BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs)
