"""Tests for format readers."""

from pathlib import Path

import pandas as pd
import pytest

from data_manager.readers import read_csv, read_json, read_parquet

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


def test_read_csv(tmp_path: Path):
    path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1, 2]}).to_csv(path, index=False)
    df = read_csv(path)
    assert list(df.columns) == ["a"]
    assert len(df) == 2


def test_read_json(tmp_path: Path):
    path = tmp_path / "sample.json"
    pd.DataFrame({"a": [1, 2]}).to_json(path, orient="records")
    df = read_json(path)
    assert len(df) == 2


@pytest.mark.skipif(not HAS_PARQUET, reason="Parquet engine not installed")
def test_read_parquet(tmp_path: Path):
    path = tmp_path / "sample.parquet"
    pd.DataFrame({"a": [1, 2]}).to_parquet(path)
    df = read_parquet(path)
    assert len(df) == 2


def test_read_csv_fallback_skips_bad_lines(tmp_path: Path):
    path = tmp_path / "broken.csv"
    path.write_text(
        "id,text\n"
        "1,ok\n"
        "2,\"still ok\"\n"
        "3,broken,row,with,too,many,fields\n"
        "4,ok again\n",
        encoding="utf-8",
    )

    df = read_csv(path)
    assert len(df) == 3
    assert list(df["id"]) == [1, 2, 4]
