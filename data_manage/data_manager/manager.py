"""Main DataManager class."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd

from .config import DEFAULT_BASE_PATH, SUPPORTED_READ_FORMATS, SUPPORTED_WRITE_FORMATS
from .exceptions import DataLoadError, DataSaveError, FileNotFoundError, UnsupportedFormatError
from .metadata import calculate_checksum, save_sidecar_metadata
from .readers import READER_MAP
from .writers import WRITER_MAP

logger = logging.getLogger(__name__)


class DataManager:
    """Unified data manager for multiple file formats.

    Attributes:
        base_path: Root directory for data files.
    """

    def __init__(self, base_path: Union[str, Path] = DEFAULT_BASE_PATH):
        """Initialize DataManager.

        Args:
            base_path: Base directory for data operations.
        """
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info("DataManager initialized with base_path: %s", self.base_path)

    def load(self, filename: str, **kwargs) -> pd.DataFrame:
        """Load any supported format into a DataFrame.

        Args:
            filename: Name or relative path of file to load.
            **kwargs: Format-specific arguments passed to pandas reader.

        Returns:
            pd.DataFrame with metadata in df.attrs.

        Raises:
            FileNotFoundError: If file does not exist.
            UnsupportedFormatError: If format is not supported.
            DataLoadError: If loading fails.
        """
        file_path = (self.base_path / filename).resolve()

        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_READ_FORMATS:
            raise UnsupportedFormatError(suffix, list(SUPPORTED_READ_FORMATS))

        if not file_path.exists():
            raise FileNotFoundError(str(file_path))

        logger.info("Loading %s...", file_path)

        reader = READER_MAP[suffix]
        try:
            df = reader(file_path, **kwargs)
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(str(file_path), str(e)) from e

        df.attrs.update(
            {
                "source_file": str(file_path),
                "loaded_at": datetime.now(),
                "row_count": len(df),
                "checksum": calculate_checksum(file_path),
            }
        )

        logger.info("Loaded %s rows from %s", len(df), file_path)
        return df

    def save(self, df: pd.DataFrame, filename: str, **kwargs) -> None:
        """Save DataFrame to any supported format.

        Args:
            df: DataFrame to save.
            filename: Output filename.
            **kwargs: Format-specific arguments passed to pandas writer.

        Raises:
            UnsupportedFormatError: If format is not supported.
            DataSaveError: If saving fails.
        """
        file_path = (self.base_path / filename).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        suffix = file_path.suffix.lower()
        if suffix not in SUPPORTED_WRITE_FORMATS:
            raise UnsupportedFormatError(suffix, list(SUPPORTED_WRITE_FORMATS))

        logger.info("Saving %s rows to %s...", len(df), file_path)

        writer = WRITER_MAP[suffix]
        try:
            writer(df, file_path, **kwargs)
        except DataSaveError:
            raise
        except Exception as e:
            raise DataSaveError(str(file_path), str(e)) from e

        if suffix in (".csv", ".json"):
            save_sidecar_metadata(df.attrs, file_path)

        logger.info("Saved to %s", file_path)

    def get_info(self, filename: str) -> Dict[str, Any]:
        """Get file metadata without loading full data.

        Args:
            filename: Name or relative path of file.

        Returns:
            Dictionary with file info (path, size, modified, row_count, etc.).
        """
        file_path = (self.base_path / filename).resolve()

        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}

        stat = file_path.stat()
        info: Dict[str, Any] = {
            "path": str(file_path),
            "size_mb": round(stat.st_size / (1024 * 1024), 4),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix.lower(),
        }

        suffix = file_path.suffix.lower()
        try:
            if suffix == ".parquet":
                import pyarrow.parquet as pq

                info["row_count"] = pq.read_metadata(file_path).num_rows
            elif suffix == ".csv":
                with open(file_path, "r", encoding="utf-8") as f:
                    info["row_count"] = max(sum(1 for _ in f) - 1, 0)
            elif suffix in (".xlsx", ".xls"):
                info["row_count"] = pd.read_excel(file_path).shape[0]
        except Exception as e:
            info["row_count_error"] = str(e)

        return info

    def list_files(self, pattern: str = "*") -> list:
        """List data files in base_path matching pattern.

        Args:
            pattern: Glob pattern (e.g., "*.csv", "data/*.parquet").

        Returns:
            List of Path objects.
        """
        return list(self.base_path.glob(pattern))
