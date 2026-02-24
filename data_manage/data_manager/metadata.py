"""Metadata handling: checksums and sidecar files."""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def calculate_checksum(path: Path, chunk_size: int = 8192) -> str:
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def serialize_metadata(attrs: Dict[str, Any]) -> Dict[str, Any]:
    """Convert DataFrame attrs to JSON-serializable dict."""
    serialized: Dict[str, Any] = {}
    for key, value in attrs.items():
        if isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif hasattr(value, "__dict__"):
            serialized[key] = str(value)
        else:
            try:
                json.dumps(value)
                serialized[key] = value
            except (TypeError, ValueError):
                serialized[key] = str(value)
    return serialized


def save_sidecar_metadata(attrs: Dict[str, Any], path: Path) -> None:
    """Save metadata to sidecar JSON file."""
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    serialized = serialize_metadata(attrs)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(serialized, f, indent=2, ensure_ascii=False)

    logger.debug("Saved metadata to %s", meta_path)


def load_sidecar_metadata(path: Path) -> Dict[str, Any]:
    """Load metadata from sidecar JSON file."""
    meta_path = path.with_suffix(path.suffix + ".meta.json")

    if not meta_path.exists():
        return {}

    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)
