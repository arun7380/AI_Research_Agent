import io
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def setup_tesseract():
    """
    Auto-detects Tesseract OCR executable path on Windows and configures pytesseract.
    """
    try:
        import pytesseract

        # 1. Check settings or environment
        from config.settings import settings
        tess_cmd = getattr(settings, "TESSERACT_CMD", None) or os.environ.get("TESSERACT_CMD")
        if tess_cmd and os.path.exists(tess_cmd):
            pytesseract.pytesseract.tesseract_cmd = tess_cmd
            return pytesseract

        # 2. Check system PATH
        which_tess = shutil.which("tesseract")
        if which_tess:
            pytesseract.pytesseract.tesseract_cmd = which_tess
            return pytesseract

        # 3. Check common Windows installation paths
        windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
        ]

        for p in windows_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                logger.info(f"Auto-detected Tesseract OCR at: {p}")
                return pytesseract

        return pytesseract
    except Exception as e:
        logger.debug(f"Pytesseract setup notice: {e}")
        return None


def extract_ocr_from_pil_image(image) -> str:
    """
    Performs OCR text extraction on a PIL Image object.
    """
    pytesseract = setup_tesseract()
    if not pytesseract:
        return ""

    try:
        text = pytesseract.image_to_string(image)
        return text.strip() if text else ""
    except Exception as e:
        logger.warning(f"Tesseract image_to_string error: {e}")
        return ""


def extract_ocr_from_pdf(file_path: str) -> Dict[str, Any]:
    """
    Performs PyMuPDF pixmap rendering and OCR on scanned PDF pages without needing pdf2image/poppler.
    Returns page text dict and extracted features.
    """
    extracted_pages = []
    full_text = ""

    try:
        import fitz  # PyMuPDF
        from PIL import Image

        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            pil_img = Image.open(io.BytesIO(img_bytes))

            ocr_text = extract_ocr_from_pil_image(pil_img)
            img_count = len(page.get_images())

            page_header = f"--- Page {i+1} (Scanned Image/OCR) ---"
            feature_meta = f"[Page Features: {pix.width}x{pix.height} px, {img_count} embedded images]"

            page_content = f"{page_header}\n{feature_meta}\n"
            if ocr_text:
                page_content += f"\nExtracted OCR Text:\n{ocr_text}\n"
            else:
                page_content += "\n[Visual Content: Image/Diagram PDF page processed]\n"

            extracted_pages.append({
                "page": i + 1,
                "text": page_content,
                "width": pix.width,
                "height": pix.height,
                "image_count": img_count
            })

            full_text += f"\n\n{page_content}"

    except Exception as e:
        logger.error(f"PyMuPDF OCR extraction error for {file_path}: {e}")

    return {
        "text": full_text.strip(),
        "pages": extracted_pages
    }


def extract_features_from_image(file_path: str) -> Dict[str, Any]:
    """
    Extracts text, visual features, and metadata from direct image files (.png, .jpg, .webp, etc.).
    """
    path = Path(file_path)
    filename = path.name

    try:
        from PIL import Image
        img = Image.open(file_path)
        width, height = img.size
        mode = img.mode
        img_format = img.format or path.suffix.lstrip(".").upper()
        file_size_kb = round(os.path.getsize(file_path) / 1024, 2)
        aspect_ratio = round(width / max(1, height), 2)

        # Extract OCR text
        ocr_text = extract_ocr_from_pil_image(img)

        features_str = (
            f"--- IMAGE DOCUMENT ANALYSIS: {filename} ---\n"
            f"[Image Metadata & Features]\n"
            f"- Format: {img_format}\n"
            f"- Resolution: {width} x {height} pixels (Aspect Ratio: {aspect_ratio})\n"
            f"- Color Mode: {mode}\n"
            f"- File Size: {file_size_kb} KB\n\n"
        )

        if ocr_text:
            features_str += f"[Extracted Text / OCR Output]:\n{ocr_text}\n"
        else:
            features_str += f"[Extracted Text / OCR Output]:\n[Visual Image Artifact: {img_format} {width}x{height} - Text extraction processed]\n"

        return {
            "text": features_str.strip(),
            "pages": [{
                "page": 1,
                "text": features_str.strip(),
                "width": width,
                "height": height,
                "format": img_format,
                "mode": mode
            }],
            "metadata": {
                "width": width,
                "height": height,
                "format": img_format,
                "color_mode": mode,
                "file_size_kb": file_size_kb,
                "has_ocr_text": bool(ocr_text)
            }
        }
    except Exception as e:
        logger.error(f"Failed to extract features from image {file_path}: {e}")
        fallback_text = f"--- IMAGE DOCUMENT: {filename} ---\n[Feature Extraction Error: {str(e)}]"
        return {
            "text": fallback_text,
            "pages": [{"page": 1, "text": fallback_text}],
            "metadata": {"error": str(e)}
        }

