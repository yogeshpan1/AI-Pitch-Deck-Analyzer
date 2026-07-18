"""
OCR fallback for image-based (scanned) PDFs.

Requires system binaries beyond pip packages:
  - Tesseract OCR: https://github.com/tesseract-ocr/tesseract
  - Poppler (for pdf2image): https://poppler.freedesktop.org/

macOS:   brew install tesseract poppler
Ubuntu:  sudo apt install tesseract-ocr poppler-utils
Windows: choco install tesseract poppler
         (or download installers manually — see README)

If these aren't installed, OCR is silently skipped and the app falls
back to the "paste manually" guidance — it never crashes the app.
"""

import re

OCR_AVAILABLE = True
try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    OCR_AVAILABLE = False


def is_ocr_available() -> bool:
    """Checks both the Python packages AND the underlying system binaries."""
    if not OCR_AVAILABLE:
        return False
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_text_via_ocr(pdf_path: str, max_pages: int = 15) -> str:
    """
    Converts PDF pages to images and runs OCR on each.
    Returns cleaned text, or empty string if OCR isn't available / fails.
    """
    if not is_ocr_available():
        return ""

    try:
        images = convert_from_path(pdf_path, dpi=200, last_page=max_pages)
        text_chunks = []
        for img in images:
            text = pytesseract.image_to_string(img)
            if text.strip():
                text_chunks.append(text)

        full_text = "\n".join(text_chunks)
        cleaned = re.sub(r'\s+', ' ', full_text)
        cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned).strip()
        return cleaned
    except Exception:
        return ""