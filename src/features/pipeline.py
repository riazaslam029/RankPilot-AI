from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.config import settings
from src.features.sql_generator import FEATURE_COLUMNS

logger = get_logger(__name__)


def compute_ctr(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ctr"] = np.where(df["impressions"] > 0, df["clicks"] / df["impressions"], 0.0)
    return df


def compute_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["page", "date"]).reset_index(drop=True)

    for window in [30]:
        df[f"ctr_mean_{window}d"] = df.groupby("page")["ctr"].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        df[f"ctr_std_{window}d"] = df.groupby("page")["ctr"].transform(
            lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
        )
        df[f"position_mean_{window}d"] = df.groupby("page")["position"].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        df[f"position_std_{window}d"] = df.groupby("page")["position"].transform(
            lambda x: x.rolling(window=window, min_periods=1).std().fillna(0)
        )
        df[f"impressions_mean_{window}d"] = df.groupby("page")["impressions"].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
        df[f"clicks_mean_{window}d"] = df.groupby("page")["clicks"].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )

    df["ctr_last_7d"] = df.groupby("page")["ctr"].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    df["ctr_last_14d"] = df.groupby("page")["ctr"].transform(lambda x: x.rolling(window=14, min_periods=1).mean())
    df["ctr_last_30d"] = df.groupby("page")["ctr"].transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    df["ctr_rolling_30d"] = df.groupby("page")["ctr"].transform(lambda x: x.shift(1).rolling(window=30, min_periods=1).mean())
    df["ctr_rolling_60d"] = df.groupby("page")["ctr"].transform(lambda x: x.shift(1).rolling(window=60, min_periods=1).mean())
    df["ctr_rolling_90d"] = df.groupby("page")["ctr"].transform(lambda x: x.shift(1).rolling(window=90, min_periods=1).mean())

    df["ctr_lag_7d"] = df.groupby("page")["ctr"].shift(7).fillna(0)
    df["ctr_lag_14d"] = df.groupby("page")["ctr"].shift(14).fillna(0)
    df["ctr_lag_30d"] = df.groupby("page")["ctr"].shift(30).fillna(0)
    df["position_lag_7d"] = df.groupby("page")["position"].shift(7).fillna(0)
    df["position_lag_14d"] = df.groupby("page")["position"].shift(14).fillna(0)
    df["position_lag_30d"] = df.groupby("page")["position"].shift(30).fillna(0)
    df["impressions_lag_7d"] = df.groupby("page")["impressions"].shift(7).fillna(0)
    df["impressions_lag_14d"] = df.groupby("page")["impressions"].shift(14).fillna(0)

    df["position_trend_7d"] = df.groupby("page")["position"].transform(
        lambda x: x.rolling(window=7, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(vals.iloc[0], 1), raw=False
        )
    ).fillna(0)
    df["ctr_trend_7d"] = df.groupby("page")["ctr"].transform(
        lambda x: x.rolling(window=7, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(abs(vals.iloc[0]), 0.0001), raw=False
        )
    ).fillna(0)
    df["impressions_trend_7d"] = df.groupby("page")["impressions"].transform(
        lambda x: x.rolling(window=7, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(vals.iloc[0], 1), raw=False
        )
    ).fillna(0)
    df["clicks_trend_7d"] = df.groupby("page")["clicks"].transform(
        lambda x: x.rolling(window=7, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(vals.iloc[0], 1), raw=False
        )
    ).fillna(0)

    return df




def compute_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df["click_growth_rate"] = df.groupby("page")["clicks"].transform(
        lambda x: x.pct_change(7).fillna(0)
    )
    df["impression_growth_rate"] = df.groupby("page")["impressions"].transform(
        lambda x: x.pct_change(7).fillna(0)
    )
    df["click_velocity_30d"] = df.groupby("page")["clicks"].transform(
        lambda x: x.rolling(window=30, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(len(vals) - 1, 1), raw=False
        )
    ).fillna(0)
    df["impression_velocity_30d"] = df.groupby("page")["impressions"].transform(
        lambda x: x.rolling(window=30, min_periods=2).apply(
            lambda vals: (vals.iloc[-1] - vals.iloc[0]) / max(len(vals) - 1, 1), raw=False
        )
    ).fillna(0)
    df["ctr_consistency"] = df.groupby("page")["ctr"].transform(
        lambda x: x.rolling(window=30, min_periods=2).std() / x.rolling(window=30, min_periods=2).mean().replace(0, 1)
    ).fillna(0)
    return df


def compute_interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["CTR_X_LOG_IMPRESSIONS"] = df["ctr"] * np.log(df["impressions"] + 1)
    df["POSITION_X_LOG_IMPRESSIONS"] = df["position"] * np.log(df["impressions"] + 1)
    df["CTR_X_POSITION_TREND"] = df["ctr"] * df["position_trend_7d"].fillna(0)
    return df


def compute_content_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["position_bucket"] = pd.cut(
        df["position"],
        bins=[0, 3, 10, 20, 50, 100, 9999],
        labels=[0, 1, 2, 3, 4, 5],
    ).astype(int).fillna(0).astype(int)
    df["content_age_days"] = df.get("content_age_days", 365)
    df["content_freshness_score"] = 1.0 / (df.get("content_freshness_days", 365) + 1)
    df["word_count"] = df.get("word_count", 600)
    df["title_length"] = df.get("title_length", 45)
    df["meta_desc_length"] = df.get("meta_desc_length", 140)
    df["heading_structure_score"] = df.get("heading_structure_score", 0.5)
    df["internal_link_count"] = df.get("internal_link_count", 5)
    df["image_count"] = df.get("image_count", 2)
    df["image_to_word_ratio"] = df["image_count"] / df["word_count"].replace(0, 1)
    df["serp_feature_present"] = df.get("serp_feature_present", 0)
    df["cannibalization_flag"] = df.get("cannibalization_flag", 0)
    df["competitor_avg_position"] = df.get("competitor_avg_position", 10.0)
    return df


def compute_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["estimated_traffic"] = df["impressions"] * df["ctr"]
    df["ctr_efficiency"] = df["ctr"] * df["position"]
    df["impressions_per_query"] = df["impressions"] / df.groupby("page")["impressions"].transform("max").replace(0, 1)
    df["clicks_per_query"] = df["clicks"] / df.groupby("page")["clicks"].transform("max").replace(0, 1)

    df["dwell_time_proxy"] = df["ctr"] * (1.0 / df["position"].replace(0, 1))
    df["pogo_stick_proxy"] = (1 - df["ctr"]) * df["position"].replace(0, 1)

    df["ctr_by_position_top3"] = df["ctr"].where(df["position"] <= 3, 0)
    df["ctr_by_position_4_10"] = df["ctr"].where((df["position"] > 3) & (df["position"] <= 10), 0)
    df["ctr_by_position_11_20"] = df["ctr"].where((df["position"] > 10) & (df["position"] <= 20), 0)
    df["ctr_by_position_21_50"] = df["ctr"].where((df["position"] > 20) & (df["position"] <= 50), 0)
    df["ctr_by_position_gt50"] = df["ctr"].where(df["position"] > 50, 0)

    df["rank_velocity"] = (df["position"] - df["position_lag_7d"]) / df["position_lag_7d"].replace(0, 1)

    df["ctr_volatility_30d"] = df.groupby("page")["ctr"].transform(
        lambda x: x.rolling(window=30, min_periods=2).std().fillna(0)
    )
    df["ctr_cv_30d"] = df["ctr_volatility_30d"] / df["ctr_mean_30d"].replace(0, 1)
    df["position_volatility_30d"] = df.groupby("page")["position"].transform(
        lambda x: x.rolling(window=30, min_periods=2).std().fillna(0)
    )

    df["historical_ctr_mean_90d"] = df.groupby("page")["ctr"].transform(
        lambda x: x.rolling(window=90, min_periods=1).mean()
    )
    df["historical_ctr_std_90d"] = df.groupby("page")["ctr"].transform(
        lambda x: x.rolling(window=90, min_periods=1).std().fillna(0)
    )
    df["impression_to_click_lag_days"] = (df["impressions_lag_7d"] - df["impressions_lag_14d"]).abs()

    return df


def run_feature_pipeline(input_path: str, output_path: str) -> str:
    logger.info("Starting feature engineering pipeline")
    df = pd.read_parquet(input_path) if input_path.endswith(".parquet") else pd.read_csv(input_path)
    logger.info(f"Loaded {len(df)} rows")

    df = compute_ctr(df)
    df = compute_rolling_features(df)
    df = compute_lag_features(df)
    df = compute_temporal_features(df)
    df = compute_interaction_features(df)
    df = compute_content_features(df)
    df = compute_derived_features(df)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(str(out), index=False, compression="snappy")
    logger.info(f"Feature engineering complete: {len(df)} rows, {len(df.columns)} features")
    return str(out)
