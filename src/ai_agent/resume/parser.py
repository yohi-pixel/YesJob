"""Extract raw text from uploaded PDF / DOCX files."""

from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile


async def extract_text(file: UploadFile) -> str:
    """Accept a PDF or DOCX upload and return extracted plain text."""
    suffix = Path(file.filename or "").suffix.lower()

    # Read bytes once
    body = await file.read()

    if suffix == ".pdf":
        return _extract_pdf(body)
    elif suffix in (".docx", ".doc"):
        return _extract_docx(body)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


# ── PDF ─────────────────────────────────────────────────

def _extract_pdf(data: bytes) -> str:
    import io

    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError(
            "pdfplumber is required for PDF parsing. "
            "Install it: pip install pdfplumber"
        )

    lines: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines.append(text.strip())
    return "\n".join(lines)


# ── DOCX ────────────────────────────────────────────────

def _extract_docx(data: bytes) -> str:
    import io

    try:
        from docx import Document
    except ImportError:
        raise RuntimeError(
            "python-docx is required for DOCX parsing. "
            "Install it: pip install python-docx"
        )

    doc = Document(io.BytesIO(data))
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
