"""Utility helpers for Data Manager."""

from pathlib import Path
from typing import Union


def resolve_path(base_path: Path, filename: Union[str, Path]) -> Path:
    """Resolve a filename against a base path."""
    return (base_path / filename).resolve()
