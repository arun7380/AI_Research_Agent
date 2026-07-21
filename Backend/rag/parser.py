import logging
from pathlib import Path
from typing import Dict, Any

from rag.ocr import extract_ocr_from_pdf

logger = logging.getLogger(__name__)


class DocumentParser:
    """
    Parses PDF, DOCX, and TXT files to extract text and page metadata.
    """

    @staticmethod
    def parse(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif ext == ".docx":
            return DocumentParser._parse_docx(file_path)
        elif ext in [".txt", ".md", ".csv"]:
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    @staticmethod
    def _parse_pdf(file_path: str) -> Dict[str, Any]:
        extracted_pages = []
        full_text = ""

        # Try PyMuPDF (fitz)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    extracted_pages.append({
                        "page": page_num + 1,
                        "text": text
                    })
                    full_text += f"\n--- Page {page_num + 1} ---\n" + text
        except Exception as e:
            logger.warning(f"PyMuPDF failed on {file_path}: {e}")

        # Fallback to pdfplumber / pypdf if empty
        if not full_text.strip():
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        extracted_pages.append({
                            "page": page_num + 1,
                            "text": text
                        })
                        full_text += f"\n--- Page {page_num + 1} ---\n" + text
            except Exception as e:
                logger.warning(f"pypdf failed on {file_path}: {e}")

        # Fallback to OCR if scanned/empty
        if not full_text.strip():
            ocr_text = extract_ocr_from_pdf(file_path)
            if ocr_text:
                full_text = ocr_text
                extracted_pages.append({"page": 1, "text": ocr_text})

        return {
            "text": full_text.strip(),
            "pages": extracted_pages,
            "metadata": {
                "total_pages": len(extracted_pages),
                "is_ocr": not extracted_pages or "OCR" in full_text
            }
        }

    @staticmethod
    def _parse_docx(file_path: str) -> Dict[str, Any]:
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            return {
                "text": full_text,
                "pages": [{"page": 1, "text": full_text}],
                "metadata": {"paragraphs": len(doc.paragraphs)}
            }
        except Exception as e:
            logger.error(f"Failed to parse DOCX {file_path}: {e}")
            raise

    @staticmethod
    def _parse_txt(file_path: str) -> Dict[str, Any]:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        return {
            "text": text,
            "pages": [{"page": 1, "text": text}],
            "metadata": {"char_count": len(text)}
        }
