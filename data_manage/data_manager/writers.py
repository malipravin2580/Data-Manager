"""Format-specific writer functions."""

from pathlib import Path

import pandas as pd

from .exceptions import DataSaveError


def write_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write DataFrame to CSV."""
    from .config import WRITER_DEFAULTS

    defaults = WRITER_DEFAULTS[".csv"].copy()
    defaults.update(kwargs)

    try:
        df.to_csv(path, **defaults)
    except Exception as e:
        raise DataSaveError(str(path), f"CSV write error: {e}") from e


def write_json(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write DataFrame to JSON."""
    from .config import WRITER_DEFAULTS

    defaults = WRITER_DEFAULTS[".json"].copy()
    defaults.update(kwargs)

    try:
        df.to_json(path, **defaults)
    except Exception as e:
        raise DataSaveError(str(path), f"JSON write error: {e}") from e


def write_excel(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write DataFrame to Excel."""
    from .config import WRITER_DEFAULTS

    defaults = WRITER_DEFAULTS[".xlsx"].copy()
    defaults.update(kwargs)

    try:
        df.to_excel(path, **defaults)
    except Exception as e:
        raise DataSaveError(str(path), f"Excel write error: {e}") from e


def write_parquet(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write DataFrame to Parquet."""
    from .config import WRITER_DEFAULTS

    defaults = WRITER_DEFAULTS[".parquet"].copy()
    defaults.update(kwargs)

    try:
        df.to_parquet(path, **defaults)
    except Exception as e:
        raise DataSaveError(str(path), f"Parquet write error: {e}") from e


def write_feather(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write DataFrame to Feather."""
    from .config import WRITER_DEFAULTS

    defaults = WRITER_DEFAULTS[".feather"].copy()
    defaults.update(kwargs)

    try:
        df.to_feather(path, **defaults)
    except Exception as e:
        raise DataSaveError(str(path), f"Feather write error: {e}") from e


# Writer mapping
WRITER_MAP = {
    ".csv": write_csv,
    ".json": write_json,
    ".xlsx": write_excel,
    ".xls": write_excel,
    ".parquet": write_parquet,
    ".feather": write_feather,
}
