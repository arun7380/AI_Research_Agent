"""
Common helper functions used throughout the application.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile


# =====================================================
# UUID Helpers
# =====================================================

def generate_uuid() -> str:
    """
    Generate a UUID4 string.
    """
    return str(uuid.uuid4())


# =====================================================
# Timestamp Helpers
# =====================================================

def current_timestamp() -> datetime:
    """
    Return current UTC timestamp.
    """
    return datetime.utcnow()


# =====================================================
# File Helpers
# =====================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


def get_file_extension(filename: str) -> str:
    """
    Return file extension in lowercase.
    """
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """
    Check whether uploaded file type is supported.
    """
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def generate_unique_filename(filename: str) -> str:
    """
    Generate unique filename while preserving extension.
    """
    extension = get_file_extension(filename)
    return f"{uuid.uuid4().hex}{extension}"


def get_file_size(file: UploadFile) -> int:
    """
    Return uploaded file size in bytes.
    """
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    return size


# =====================================================
# Text Helpers
# =====================================================

def clean_text(text: str) -> str:
    """
    Basic text cleaning.
    """
    return " ".join(text.split())


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate long text.
    """
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."


# =====================================================
# Token Estimation
# =====================================================

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation.

    Approximately:
    1 token ≈ 4 characters
    """
    return max(1, len(text) // 4)


# =====================================================
# Formatting Helpers
# =====================================================

def format_bytes(size: int) -> str:
    """
    Convert bytes into readable format.
    """

    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


def success_response(message: str, data=None):
    """
    Standard success response.
    """

    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str):
    """
    Standard error response.
    """

    return {
        "success": False,
        "message": message,
    }