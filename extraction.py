import io
import streamlit as st

# Optional DOCX support
# Tries to load the python-docx dependency to enable DOCX file extraction.
# If the library is not installed, DOCX support is gracefully disabled
# instead of crashing the application.
try:
    import docx
    HAS_DOCX = True
except Exception:
    docx = None
    HAS_DOCX = False

"""
File: extraction.py

Responsibility:
Extract plain text from user-uploaded CV and Job Description files.

Supported formats:
- PDF (via PyPDF2)
- DOCX (via python-docx)
- TXT (UTF-8 decoded)

Purpose:
This module converts uploaded documents into a normalized plain-text
representation so the content can be safely validated, truncated, and
embedded into LLM prompts.

Design notes:
- Isolated file-processing logic (no UI, no prompt logic, no LLM calls)
- Fault-tolerant: returns empty strings if extraction fails
- Enables clean separation between file I/O and application logic
"""

def _extract_pdf(bytes_data: bytes) -> str:
    try:
        import PyPDF2
    except Exception:
        st.warning(
            "PyPDF2 not installed. PDF extraction unavailable.\n"
            "Install in the project venv and restart Streamlit:\n"
            ".\\.venv\\Scripts\\Activate.ps1; then python -m pip install PyPDF2"
        )
        return ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(bytes_data))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception:
        return ""


def _extract_docx(bytes_data: bytes) -> str:
    if not HAS_DOCX:
        return ""
    try:
        doc = docx.Document(io.BytesIO(bytes_data))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def extract_text(uploaded) -> str:
    if uploaded is None:
        return ""
    try:
        # Prefer getvalue(); fallback to read() if unavailable
        data = uploaded.getvalue() if hasattr(uploaded, "getvalue") else uploaded.read()
    except Exception:
        return ""
    name = getattr(uploaded, "name", "").lower()
    if name.endswith(".pdf"):
        return _extract_pdf(data)
    if name.endswith(".docx") or name.endswith(".doc"):
        if not HAS_DOCX:
            st.warning("DOCX support missing. Install: python -m pip install python-docx")
            return ""
        return _extract_docx(data)
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

# ==============================================
# File text extraction
# - PDF (PyPDF2), DOCX (python-docx), TXT
# ==============================================