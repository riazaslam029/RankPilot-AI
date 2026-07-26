import pytest
import pandas as pd
import numpy as np

from src.features.pipeline import (
    compute_ctr,
    compute_rolling_features,
    compute_lag_features,
    compute_temporal_features,
    compute_interaction_features,
    compute_content_features,
    compute_derived_features,
    run_feature_pipeline,
    FEATURE_COUNT,
)
from src.features.sql_generator import FEATURE_COLUMNS


@pytest.fixture
def minimal_dataframe():
    n = 100
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    df = pd.DataFrame({
        "page": [f"/test-page"] * n,
        "date": dates,
        "impressions": np.random.randint(100, 10000, n),
        "clicks": np.random.randint(0, 500, n),
        "position": np.random.uniform(1, 50, n).round(2),
    })
    df["ctr"] = (df["clicks"] / df["impressions"] * 100).clip(0.001, 50)
    df["ctr"] = df["ctr"].round(4)
    return df


def test_compute_ctr(minimal_dataframe):
    result = compute_ctr(minimal_dataframe)
    assert "ctr" in result.columns
    assert (result["ctr"] >= 0).all()


def test_compute_rolling_features(minimal_dataframe):
    result = compute_rolling_features(minimal_dataframe)
    assert "ctr_mean_30d" in result.columns
    assert "ctr_trend_7d" in result.columns
    assert "position_mean_30d" in result.columns
    assert "position_trend_7d" in result.columns


def test_compute_lag_features(minimal_dataframe):
    result = compute_lag_features(minimal_dataframe)
    assert "ctr_lag_7d" in result.columns
    assert "ctr_lag_14d" in result.columns
    assert "position_lag_7d" in result.columns


def test_compute_temporal_features(minimal_dataframe):
    result = compute_temporal_features(minimal_dataframe)
    assert "click_growth_rate" in result.columns
    assert "impression_growth_rate" in result.columns


def test_compute_interaction_features(minimal_dataframe):
    result = compute_interaction_features(minimal_dataframe)
    assert "CTR_X_LOG_IMPRESSIONS" in result.columns
    assert "POSITION_X_LOG_IMPRESSIONS" in result.columns
    assert "CTR_X_POSITION_TREND" in result.columns


def test_compute_derived_features(minimal_dataframe):
    result = compute_derived_features(minimal_dataframe)
    assert "estimated_traffic" in result.columns
    assert "ctr_efficiency" in result.columns
    assert "rank_velocity" in result.columns


def test_feature_column_count():
    assert FEATURE_COUNT == 69, f"Expected 69 defined columns, got {FEATURE_COUNT}"


def test_full_pipeline(minimal_dataframe, tmp_path):
    input_path = str(tmp_path / "input.parquet")
    output_path = str(tmp_path / "output.parquet")
    minimal_dataframe.to_parquet(input_path)

    result = run_feature_pipeline(input_path, output_path)
    assert Path(result).exists()

    result_df = pd.read_parquet(result)
    assert len(result_df) > 0
    assert "ctr" in result_df.columns
