from __future__ import annotations

FEATURE_COLUMNS = [
    "ctr_mean_30d",
    "ctr_std_30d",
    "ctr_trend_7d",
    "position_mean_30d",
    "position_std_30d",
    "position_trend_7d",
    "impressions_mean_30d",
    "impressions_trend_7d",
    "clicks_mean_30d",
    "clicks_trend_7d",
    "ctr_last_7d",
    "ctr_last_14d",
    "ctr_last_30d",
    "ctr_rolling_30d",
    "ctr_rolling_60d",
    "ctr_rolling_90d",
    "ctr_lag_7d",
    "ctr_lag_14d",
    "ctr_lag_30d",
    "position_lag_7d",
    "position_lag_14d",
    "position_lag_30d",
    "impressions_lag_7d",
    "impressions_lag_14d",
    "impressions_per_query",
    "clicks_per_query",
    "estimated_traffic",
    "ctr_efficiency",
    "click_growth_rate",
    "impression_growth_rate",
    "position_volatility_30d",
    "ctr_volatility_30d",
    "ctr_cv_30d",
    "historical_ctr_mean_90d",
    "historical_ctr_std_90d",
    "content_age_days",
    "content_freshness_score",
    "word_count",
    "title_length",
    "meta_desc_length",
    "heading_structure_score",
    "internal_link_count",
    "image_count",
    "image_to_word_ratio",
    "position_bucket",
    "category_rank_percentile",
    "category_impression_share",
    "serp_feature_present",
    "cannibalization_flag",
    "competitor_avg_position",
    "dwell_time_proxy",
    "pogo_stick_proxy",
    "click_velocity_30d",
    "impression_velocity_30d",
    "ctr_consistency",
    "impression_to_click_lag_days",
    "query_diversity",
    "rank_velocity",
    "ctr_by_position_top3",
    "ctr_by_position_4_10",
    "ctr_by_position_11_20",
    "ctr_by_position_21_50",
    "ctr_by_position_gt50",
    "CTR_X_LOG_IMPRESSIONS",
    "POSITION_X_LOG_IMPRESSIONS",
    "CTR_X_POSITION_TREND",
]

FEATURE_COUNT = len(FEATURE_COLUMNS)


def build_feature_sql(source_table: str = "sp") -> str:
    return f"""
    WITH daily_stats AS (
        SELECT
            page,
            date,
            SUM(impressions) AS impressions,
            SUM(clicks) AS clicks,
            CASE WHEN SUM(impressions) > 0 THEN SUM(clicks) * 1.0 / SUM(impressions) ELSE 0.0 END AS ctr,
            AVG(position) AS position
        FROM {source_table}
        GROUP BY page, date
    ),
    rolling AS (
        SELECT
            page,
            date,
            impressions,
            clicks,
            ctr,
            position,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS ctr_mean_30d,
            STDDEV(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS ctr_std_30d,
            AVG(position) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS position_mean_30d,
            STDDEV(position) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS position_std_30d,
            AVG(impressions) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
            ) AS impressions_mean_30d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ) AS ctr_last_7d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 13 PRECEDING AND 7 PRECEDING
            ) AS ctr_last_14d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 29 PRECEDING AND 15 PRECEDING
            ) AS ctr_last_30d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 14 PRECEDING AND 1 PRECEDING
            ) AS ctr_rolling_30d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 59 PRECEDING AND 30 PRECEDING
            ) AS ctr_rolling_60d,
            AVG(ctr) OVER (
                PARTITION BY page ORDER BY date
                ROWS BETWEEN 89 PRECEDING AND 60 PRECEDING
            ) AS ctr_rolling_90d,
            LAG(ctr, 7) OVER (PARTITION BY page ORDER BY date) AS ctr_lag_7d,
            LAG(ctr, 14) OVER (PARTITION BY page ORDER BY date) AS ctr_lag_14d,
            LAG(ctr, 30) OVER (PARTITION BY page ORDER BY date) AS ctr_lag_30d,
            LAG(position, 7) OVER (PARTITION BY page ORDER BY date) AS position_lag_7d,
            LAG(position, 14) OVER (PARTITION BY page ORDER BY date) AS position_lag_14d,
            LAG(position, 30) OVER (PARTITION BY page ORDER BY date) AS position_lag_30d,
            LAG(impressions, 7) OVER (PARTITION BY page ORDER BY date) AS impressions_lag_7d,
            LAG(impressions, 14) OVER (PARTITION BY page ORDER BY date) AS impressions_lag_14d,
            COUNT(*) OVER (PARTITION BY page) AS query_diversity,
            SUM(impressions) OVER (PARTITION BY page) AS total_impressions,
            SUM(clicks) OVER (PARTITION BY page) AS total_clicks
        FROM daily_stats
    ),
    daily_slope AS (
        SELECT
            page,
            date,
            impressions,
            clicks,
            ctr,
            position,
            ctr_mean_30d,
            ctr_std_30d,
            position_mean_30d,
            position_std_30d,
            impressions_mean_30d,
            ctr_last_7d,
            ctr_last_14d,
            ctr_last_30d,
            ctr_rolling_30d,
            ctr_rolling_60d,
            ctr_rolling_90d,
            ctr_lag_7d,
            ctr_lag_14d,
            ctr_lag_30d,
            position_lag_7d,
            position_lag_14d,
            position_lag_30d,
            impressions_lag_7d,
            impressions_lag_14d,
            query_diversity,
            total_impressions,
            total_clicks,
            CASE WHEN COUNT(*) OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) >= 2
                THEN REGR_SLOPE(ctr, ROW_NUMBER() OVER (PARTITION BY page ORDER BY date))
                     OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ELSE 0.0 END AS ctr_trend_7d,
            CASE WHEN COUNT(*) OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) >= 2
                THEN REGR_SLOPE(position, ROW_NUMBER() OVER (PARTITION BY page ORDER BY date))
                     OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ELSE 0.0 END AS position_trend_7d,
            CASE WHEN COUNT(*) OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) >= 2
                THEN REGR_SLOPE(impressions, ROW_NUMBER() OVER (PARTITION BY page ORDER BY date))
                     OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ELSE 0.0 END AS impressions_trend_7d,
            CASE WHEN COUNT(*) OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) >= 2
                THEN REGR_SLOPE(clicks, ROW_NUMBER() OVER (PARTITION BY page ORDER BY date))
                     OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                ELSE 0.0 END AS clicks_trend_7d,
            CASE WHEN COUNT(*) OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) >= 2
                THEN REGR_SLOPE(ctr, ROW_NUMBER() OVER (PARTITION BY page ORDER BY date))
                     OVER (PARTITION BY page ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)
                ELSE 0.0 END AS ctr_trend_30d,
        FROM rolling
    )
    SELECT
        page,
        date,
        impressions,
        clicks,
        ctr,
        position,
        ctr_mean_30d,
        ctr_std_30d,
        ctr_trend_7d,
        position_mean_30d,
        position_std_30d,
        position_trend_7d,
        impressions_mean_30d,
        impressions_trend_7d,
        clicks_mean_30d,
        clicks_trend_7d,
        ctr_last_7d,
        ctr_last_14d,
        ctr_last_30d,
        ctr_rolling_30d,
        ctr_rolling_60d,
        ctr_rolling_90d,
        ctr_lag_7d,
        ctr_lag_14d,
        ctr_lag_30d,
        position_lag_7d,
        position_lag_14d,
        position_lag_30d,
        impressions_lag_7d,
        impressions_lag_14d,
        impressions_per_query,
        clicks_per_query,
        estimated_traffic,
        ctr_efficiency,
        click_growth_rate,
        impression_growth_rate,
        position_volatility_30d,
        ctr_volatility_30d,
        ctr_cv_30d,
        historical_ctr_mean_90d,
        historical_ctr_std_90d,
        content_age_days,
        content_freshness_score,
        word_count,
        title_length,
        meta_desc_length,
        heading_structure_score,
        internal_link_count,
        image_count,
        image_to_word_ratio,
        position_bucket,
        category_rank_percentile,
        category_impression_share,
        serp_feature_present,
        cannibalization_flag,
        competitor_avg_position,
        dwell_time_proxy,
        pogo_stick_proxy,
        click_velocity_30d,
        impression_velocity_30d,
        ctr_consistency,
        impression_to_click_lag_days,
        query_diversity,
        rank_velocity,
        ctr_by_position_top3,
        ctr_by_position_4_10,
        ctr_by_position_11_20,
        ctr_by_position_21_50,
        ctr_by_position_gt50,
        CTR_X_LOG_IMPRESSIONS,
        POSITION_X_LOG_IMPRESSIONS,
        CTR_X_POSITION_TREND,
    FROM daily_slope
    """.strip()
