"""Tests for format writers."""

from pathlib import Path

import pandas as pd
import pytest

from data_manager.writers import write_csv, write_json, write_parquet

HAS_PARQUET = False
try:
    import pyarrow  # noqa: F401

    HAS_PARQUET = True
except Exception:
    try:
        import fastparquet  # noqa: F401

        HAS_PARQUET = True
    except Exception:
        HAS_PARQUET = False


def test_write_csv(tmp_path: Path):
    path = tmp_path / "out.csv"
    write_csv(pd.DataFrame({"a": [1]}), path)
    assert path.exists()


def test_write_json(tmp_path: Path):
    path = tmp_path / "out.json"
    write_json(pd.DataFrame({"a": [1]}), path)
    assert path.exists()


@pytest.mark.skipif(not HAS_PARQUET, reason="Parquet engine not installed")
def test_write_parquet(tmp_path: Path):
    path = tmp_path / "out.parquet"
    write_parquet(pd.DataFrame({"a": [1]}), path)
    assert path.exists()
