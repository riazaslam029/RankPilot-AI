from __future__ import annotations

from pathlib import Path

import duckdb

from src.utils.logging import get_logger
from src.utils.config import settings

logger = get_logger(__name__)


def get_connection(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    path = db_path or str(settings.duckdb_path)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))
    con.execute("SET threads TO 4")
    con.execute("SET memory_limit='2GB'")
    logger.info(f"Connected to DuckDB at {path}")
    return con


def execute_query(con: duckdb.DuckDBPyConnection, query: str) -> any:
    logger.debug(f"Executing query: {query[:200]}...")
    return con.execute(query)


def initialize_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS search_performance (
            date DATE,
            page VARCHAR,
            queries_str VARCHAR,
            impressions BIGINT,
            clicks BIGINT,
            ctr DOUBLE,
            position DOUBLE,
            site VARCHAR,
            country VARCHAR DEFAULT 'US',
            device VARCHAR DEFAULT 'desktop',
            source VARCHAR DEFAULT 'google_search_console'
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS page_metadata (
            page VARCHAR PRIMARY KEY,
            url VARCHAR,
            title VARCHAR,
            h1 VARCHAR,
            word_count INTEGER,
            content_freshness_days INTEGER,
            last_modified DATE,
            canonical_url VARCHAR,
            status_code INTEGER,
            schema_type VARCHAR,
            internal_links INTEGER,
            external_links INTEGER,
            images INTEGER,
            word_count_estimated INTEGER
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS features (
            page VARCHAR,
            date DATE,
            ctr_mean_30d DOUBLE,
            ctr_std_30d DOUBLE,
            ctr_trend_7d DOUBLE,
            position_mean_30d DOUBLE,
            position_std_30d DOUBLE,
            position_trend_7d DOUBLE,
            impressions_mean_30d DOUBLE,
            impressions_trend_7d DOUBLE,
            clicks_mean_30d DOUBLE,
            clicks_trend_7d DOUBLE,
            ctr_last_7d DOUBLE,
            ctr_last_14d DOUBLE,
            ctr_last_30d DOUBLE,
            ctr_rolling_30d DOUBLE,
            ctr_rolling_60d DOUBLE,
            ctr_rolling_90d DOUBLE,
            ctr_lag_7d DOUBLE,
            ctr_lag_14d DOUBLE,
            ctr_lag_30d DOUBLE,
            position_lag_7d DOUBLE,
            position_lag_14d DOUBLE,
            position_lag_30d DOUBLE,
            impressions_lag_7d DOUBLE,
            impressions_lag_14d DOUBLE,
            impressions_per_query DOUBLE,
            clicks_per_query DOUBLE,
            estimated_traffic DOUBLE,
            ctr_efficiency DOUBLE,
            click_growth_rate DOUBLE,
            impression_growth_rate DOUBLE,
            position_volatility_30d DOUBLE,
            ctr_volatility_30d DOUBLE,
            ctr_cv_30d DOUBLE,
            historical_ctr_mean_90d DOUBLE,
            historical_ctr_std_90d DOUBLE,
            content_age_days INTEGER,
            content_freshness_score DOUBLE,
            word_count INTEGER,
            title_length INTEGER,
            meta_desc_length INTEGER,
            heading_structure_score DOUBLE,
            internal_link_count INTEGER,
            image_count INTEGER,
            image_to_word_ratio DOUBLE,
            position_bucket INTEGER,
            category_rank_percentile DOUBLE,
            category_impression_share DOUBLE,
            serp_feature_present INTEGER,
            cannibalization_flag INTEGER,
            competitor_avg_position DOUBLE,
            dwell_time_proxy DOUBLE,
            pogo_stick_proxy DOUBLE,
            click_velocity_30d DOUBLE,
            impression_velocity_30d DOUBLE,
            ctr_consistency DOUBLE,
            impression_to_click_lag_days INTEGER,
            query_diversity INTEGER,
            rank_velocity DOUBLE,
            ctr_by_position_top3 DOUBLE,
            ctr_by_position_4_10 DOUBLE,
            ctr_by_position_11_20 DOUBLE,
            ctr_by_position_21_50 DOUBLE,
            ctr_by_position_gt50 DOUBLE,
            CTR_X_LOG_IMPRESSIONS DOUBLE,
            POSITION_X_LOG_IMPRESSIONS DOUBLE,
            CTR_X_POSITION_TREND DOUBLE
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            page VARCHAR,
            date DATE,
            model_version VARCHAR,
            protect_score DOUBLE,
            improve_score DOUBLE,
            refresh_score DOUBLE,
            rewrite_score DOUBLE,
            merge_score DOUBLE,
            prune_score DOUBLE,
            monitor_score DOUBLE,
            primary_action VARCHAR,
            confidence DOUBLE,
            reason_codes VARCHAR,
            priority_rank INTEGER
        )
    """)
    logger.info("DuckDB schema initialized")


def close_connection(con: duckdb.DuckDBPyConnection) -> None:
    con.close()
    logger.info("DuckDB connection closed")
