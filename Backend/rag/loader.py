from pathlib import Path
from typing import Dict, Any

class DocumentLoader:
    """
    Handles reading raw files from disk.
    """

    @staticmethod
    def load_file(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        file_bytes = path.read_bytes()

        return {
            "file_path": str(path.resolve()),
            "filename": path.name,
            "file_type": ext.lstrip("."),
            "file_size": len(file_bytes),
            "raw_bytes": file_bytes,
        }
