from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchPerformanceRow:
    date: str
    page: str
    queries_str: str = "[]"
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    position: float = 0.0
    site: str = ""
    country: str = "US"
    device: str = "desktop"
    source: str = "google_search_console"


@dataclass
class PageMetadataRow:
    page: str
    url: str = ""
    title: str = ""
    h1: str = ""
    word_count: int = 0
    content_freshness_days: int = 0
    last_modified: str = ""
    canonical_url: str = ""
    status_code: int = 200
    schema_type: str = ""
    internal_links: int = 0
    external_links: int = 0
    images: int = 0
    word_count_estimated: int = 0


@dataclass
class FeatureRow:
    page: str = ""
    date: str = ""
    ctr_mean_30d: float = 0.0
    ctr_std_30d: float = 0.0
    ctr_trend_7d: float = 0.0
    position_mean_30d: float = 0.0
    position_std_30d: float = 0.0
    position_trend_7d: float = 0.0
    impressions_mean_30d: float = 0.0
    impressions_trend_7d: float = 0.0
    clicks_mean_30d: float = 0.0
    clicks_trend_7d: float = 0.0
    ctr_last_7d: float = 0.0
    ctr_last_14d: float = 0.0
    ctr_last_30d: float = 0.0
    ctr_rolling_30d: float = 0.0
    ctr_rolling_60d: float = 0.0
    ctr_rolling_90d: float = 0.0
    ctr_lag_7d: float = 0.0
    ctr_lag_14d: float = 0.0
    ctr_lag_30d: float = 0.0
    position_lag_7d: float = 0.0
    position_lag_14d: float = 0.0
    position_lag_30d: float = 0.0
    impressions_lag_7d: float = 0.0
    impressions_lag_14d: float = 0.0
    impressions_per_query: float = 0.0
    clicks_per_query: float = 0.0
    estimated_traffic: float = 0.0
    ctr_efficiency: float = 0.0
    click_growth_rate: float = 0.0
    impression_growth_rate: float = 0.0
    position_volatility_30d: float = 0.0
    ctr_volatility_30d: float = 0.0
    ctr_cv_30d: float = 0.0
    historical_ctr_mean_90d: float = 0.0
    historical_ctr_std_90d: float = 0.0
    content_age_days: int = 0
    content_freshness_score: float = 0.0
    word_count: int = 0
    title_length: int = 0
    meta_desc_length: int = 0
    heading_structure_score: float = 0.0
    internal_link_count: int = 0
    image_count: int = 0
    image_to_word_ratio: float = 0.0
    position_bucket: int = 0
    category_rank_percentile: float = 0.0
    category_impression_share: float = 0.0
    serp_feature_present: int = 0
    cannibalization_flag: int = 0
    competitor_avg_position: float = 0.0
    dwell_time_proxy: float = 0.0
    pogo_stick_proxy: float = 0.0
    click_velocity_30d: float = 0.0
    impression_velocity_30d: float = 0.0
    ctr_consistency: float = 0.0
    impression_to_click_lag_days: int = 0
    query_diversity: int = 0
    rank_velocity: float = 0.0
    day_of_week_ctr_dev_0: float = 0.0
    day_of_week_ctr_dev_1: float = 0.0
    day_of_week_ctr_dev_2: float = 0.0
    day_of_week_ctr_dev_3: float = 0.0
    day_of_week_ctr_dev_4: float = 0.0
    day_of_week_ctr_dev_5: float = 0.0
    day_of_week_ctr_dev_6: float = 0.0
    ctr_by_position_top3: float = 0.0
    ctr_by_position_4_10: float = 0.0
    ctr_by_position_11_20: float = 0.0
    ctr_by_position_21_50: float = 0.0
    ctr_by_position_gt50: float = 0.0
    CTR_X_LOG_IMPRESSIONS: float = 0.0
    POSITION_X_LOG_IMPRESSIONS: float = 0.0
    CTR_X_POSITION_TREND: float = 0.0
