"""Tests for DataManager."""

import pandas as pd
import pytest

from data_manager import DataManager, FileNotFoundError, UnsupportedFormatError

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


@pytest.fixture
def dm(tmp_path):
    return DataManager(base_path=tmp_path)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [10.5, 20.3, 30.1],
        }
    )


def test_load_csv(dm, sample_df, tmp_path):
    csv_path = tmp_path / "test.csv"
    sample_df.to_csv(csv_path, index=False)

    df = dm.load("test.csv")

    assert len(df) == 3
    assert "source_file" in df.attrs
    assert "checksum" in df.attrs


def test_load_json(dm, sample_df, tmp_path):
    json_path = tmp_path / "test.json"
    sample_df.to_json(json_path, orient="records")

    df = dm.load("test.json")
    assert len(df) == 3


def test_load_excel(dm, sample_df, tmp_path):
    xlsx_path = tmp_path / "test.xlsx"
    sample_df.to_excel(xlsx_path, index=False)

    df = dm.load("test.xlsx")
    assert len(df) == 3


@pytest.mark.skipif(not HAS_PARQUET, reason="Parquet engine not installed")
def test_load_parquet(dm, sample_df, tmp_path):
    pq_path = tmp_path / "test.parquet"
    sample_df.to_parquet(pq_path)

    df = dm.load("test.parquet")
    assert len(df) == 3


def test_save_csv_with_metadata(dm, sample_df, tmp_path):
    dm.save(sample_df, "out.csv")

    assert (tmp_path / "out.csv").exists()
    assert (tmp_path / "out.csv.meta.json").exists()


def test_unsupported_format(dm):
    with pytest.raises(UnsupportedFormatError):
        dm.load("test.xyz")


def test_file_not_found(dm):
    with pytest.raises(FileNotFoundError):
        dm.load("nonexistent.csv")


@pytest.mark.skipif(not HAS_PARQUET, reason="Parquet engine not installed")
def test_get_info_parquet(dm, sample_df, tmp_path):
    pq_path = tmp_path / "test.parquet"
    sample_df.to_parquet(pq_path)

    info = dm.get_info("test.parquet")
    assert info["row_count"] == 3
    assert "size_mb" in info
