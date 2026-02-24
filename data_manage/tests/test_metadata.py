"""Tests for metadata helpers."""

from datetime import datetime
from pathlib import Path

from data_manager.metadata import calculate_checksum, load_sidecar_metadata, save_sidecar_metadata


def test_calculate_checksum(tmp_path: Path):
    path = tmp_path / "file.txt"
    path.write_text("abc", encoding="utf-8")
    assert calculate_checksum(path) == "900150983cd24fb0d6963f7d28e17f72"


def test_sidecar_roundtrip(tmp_path: Path):
    path = tmp_path / "out.csv"
    path.write_text("id\n1\n", encoding="utf-8")
    payload = {"created": datetime(2026, 1, 1), "owner": "qa"}

    save_sidecar_metadata(payload, path)
    loaded = load_sidecar_metadata(path)

    assert loaded["owner"] == "qa"
    assert loaded["created"].startswith("2026-01-01")
