import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.ingestion import ingest_csv, ingest_directory, prepare_for_feature_engineering
from src.data.validation import validate_search_console_csv, quarantined_rows_from_validation
from src.data.schema import SearchPerformanceRow


def test_ingest_csv_valid(sample_search_data, tmp_path):
    csv_path = tmp_path / "test_data.csv"
    sample_search_data.head(100).to_csv(str(csv_path), index=False)

    result = ingest_csv(str(csv_path))
    assert len(result) > 0
    assert "page" in result.columns
    assert "ctr" in result.columns
    assert "position" in result.columns


def test_ingest_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        ingest_csv("/nonexistent/path/data.csv")


def test_prepare_for_feature_engineering(sample_search_data):
    result = prepare_for_feature_engineering(sample_search_data)
    assert len(result) > 0
    assert "day_of_week" in result.columns
    assert result["ctr"].min() >= 0


def test_validate_search_console_csv_valid(sample_search_data, tmp_path):
    csv_path = tmp_path / "valid.csv"
    sample_search_data.head(10).to_csv(str(csv_path), index=False)

    result = validate_search_console_csv(str(csv_path))
    assert result.is_valid is True


def test_quarantined_rows_valid_data(sample_search_data, tmp_path):
    csv_path = tmp_path / "quarantine_test.csv"
    sample_search_data.head(10).to_csv(str(csv_path), index=False)

    quarantined = quarantined_rows_from_validation(str(csv_path))
    assert isinstance(quarantined, list)
