"""Format-specific reader functions."""

import logging
from pathlib import Path

import pandas as pd

from .exceptions import DataLoadError

logger = logging.getLogger(__name__)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read CSV file."""
    from .config import READER_DEFAULTS

    defaults = READER_DEFAULTS[".csv"].copy()
    defaults.update(kwargs)
    try:
        return pd.read_csv(path, **defaults)
    except Exception as e:
        # Fallback for inconsistent CSV rows often seen in exported transcripts/logs.
        fallback = defaults.copy()
        fallback.update({"engine": "python"})
        fallback.pop("low_memory", None)
        try:
            return pd.read_csv(path, on_bad_lines="skip", **fallback)
        except TypeError:
            # pandas < 1.3 compatibility
            try:
                return pd.read_csv(
                    path,
                    error_bad_lines=False,
                    warn_bad_lines=True,
                    **fallback,
                )
            except Exception as fallback_error:
                raise DataLoadError(str(path), f"CSV parse error: {fallback_error}") from fallback_error
        except Exception as fallback_error:
            raise DataLoadError(str(path), f"CSV parse error: {fallback_error}") from fallback_error


def read_json(path: Path, **kwargs) -> pd.DataFrame:
    """Read JSON file (normal or NDJSON)."""
    from .config import READER_DEFAULTS

    defaults = READER_DEFAULTS[".json"].copy()
    defaults.update(kwargs)

    try:
        return pd.read_json(path, **defaults)
    except ValueError:
        # Try as NDJSON
        logger.debug("Trying NDJSON fallback for %s", path)
        defaults_ndjson = READER_DEFAULTS[".jsonl"].copy()
        defaults_ndjson.update(kwargs)
        defaults_ndjson["lines"] = True
        try:
            return pd.read_json(path, **defaults_ndjson)
        except Exception as e:
            raise DataLoadError(str(path), f"JSON parse error: {e}") from e
    except Exception as e:
        raise DataLoadError(str(path), f"JSON parse error: {e}") from e


def read_excel(path: Path, **kwargs) -> pd.DataFrame:
    """Read Excel file."""
    from .config import READER_DEFAULTS

    suffix = path.suffix.lower()
    defaults = READER_DEFAULTS[suffix].copy()
    defaults.update(kwargs)

    try:
        return pd.read_excel(path, **defaults)
    except Exception as e:
        raise DataLoadError(str(path), f"Excel parse error: {e}") from e


def read_parquet(path: Path, **kwargs) -> pd.DataFrame:
    """Read Parquet file."""
    try:
        return pd.read_parquet(path, **kwargs)
    except Exception as e:
        raise DataLoadError(str(path), f"Parquet read error: {e}") from e


def read_feather(path: Path, **kwargs) -> pd.DataFrame:
    """Read Feather file."""
    try:
        return pd.read_feather(path, **kwargs)
    except Exception as e:
        raise DataLoadError(str(path), f"Feather read error: {e}") from e


def read_pickle(path: Path, **kwargs) -> pd.DataFrame:
    """Read Pickle file (trusted sources only)."""
    try:
        return pd.read_pickle(path, **kwargs)
    except Exception as e:
        raise DataLoadError(str(path), f"Pickle read error: {e}") from e


# Reader mapping
READER_MAP = {
    ".csv": read_csv,
    ".json": read_json,
    ".jsonl": read_json,
    ".xlsx": read_excel,
    ".xls": read_excel,
    ".parquet": read_parquet,
    ".feather": read_feather,
    ".pkl": read_pickle,
}
