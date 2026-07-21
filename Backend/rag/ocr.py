import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_ocr_from_pdf(file_path: str) -> Optional[str]:
    """
    Attempt OCR on scanned PDF pages using pytesseract and pdf2image.
    Returns extracted text if successful, or None if OCR dependencies are missing.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path

        images = convert_from_path(file_path)
        extracted_pages = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            if text.strip():
                extracted_pages.append(f"--- Page {i+1} (OCR) ---\n{text}")

        return "\n\n".join(extracted_pages) if extracted_pages else None
    except Exception as e:
        logger.warning(f"OCR extraction unavailable or failed for {file_path}: {e}")
        return None
