"""Data Manager - Unified multi-format data handling."""

from .manager import DataManager
from .exceptions import (
    DataManagerError,
    UnsupportedFormatError,
    DataLoadError,
    DataSaveError,
    FileNotFoundError,
)

__version__ = "1.0.0"
__all__ = [
    "DataManager",
    "DataManagerError",
    "UnsupportedFormatError",
    "DataLoadError",
    "DataSaveError",
    "FileNotFoundError",
]
