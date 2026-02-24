"""Configuration and constants."""

from pathlib import Path
from typing import Dict

# Default base path
DEFAULT_BASE_PATH = Path("./data")

# Supported formats
SUPPORTED_READ_FORMATS = frozenset(
    {
        ".csv",
        ".json",
        ".jsonl",
        ".xlsx",
        ".xls",
        ".parquet",
        ".feather",
        ".pkl",
    }
)

SUPPORTED_WRITE_FORMATS = frozenset({".csv", ".json", ".xlsx", ".parquet", ".feather"})

# Default reader kwargs per format
READER_DEFAULTS: Dict[str, Dict] = {
    ".csv": {"low_memory": False, "encoding": "utf-8"},
    ".json": {"orient": "records"},
    ".jsonl": {"lines": True, "orient": "records"},
    ".xlsx": {"engine": "openpyxl"},
    ".xls": {"engine": "xlrd"},
    ".parquet": {},
    ".feather": {},
    ".pkl": {},
}

# Default writer kwargs per format
WRITER_DEFAULTS: Dict[str, Dict] = {
    ".csv": {"index": False, "encoding": "utf-8"},
    ".json": {"orient": "records", "indent": 2},
    ".xlsx": {"index": False, "engine": "openpyxl"},
    ".parquet": {"compression": "snappy", "index": False},
    ".feather": {"compression": "lz4"},
}

# Metadata sidecar suffix
METADATA_SUFFIX = ".meta.json"
