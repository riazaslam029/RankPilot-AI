from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    quarantined_rows: list[int] = field(default_factory=list)


REASON_CODE_PATTERNS = {
    "HIGH_TRAFFIC_IMPACT": lambda f: f.get("impressions", 0) > 0,
    "CTR_BELOW_THRESHOLD": lambda f: f.get("ctr", 0) < 0.01 and f.get("position", 0) < 10,
    "CTR_WELL_ABOVE_AVG": lambda f: f.get("ctr", 0) > 0.05 and f.get("position", 0) <= 5,
    "POSITION_DECLINING": lambda f: f.get("position_trend_7d", 0) < -1.0 and f.get("position", 0) > 10,
    "POSITION_IMPROVING": lambda f: f.get("position_trend_7d", 0) > 1.0 and f.get("position", 0) < 20,
    "CONTENT_STALE": lambda f: f.get("content_freshness_days", 999) > 365,
    "CONTENT_FRESH": lambda f: f.get("content_freshness_days", 0) < 30,
    "TITLE_OPTIMIZATION": lambda f: (f.get("title_length", 0) > 70 or f.get("title_length", 0) < 30),
    "META_DESC_OPTIMIZATION": lambda f: (f.get("meta_desc_length", 0) > 170 or f.get("meta_desc_length", 0) < 50),
    "LOW_INTERNAL_LINKS": lambda f: f.get("internal_link_count", 10) < 3,
    "HIGH_CANNIBALIZATION": lambda f: f.get("cannibalization_flag", 0) > 2,
    "HIGH_BROWSE_DEPTH_NEEDED": lambda f: f.get("word_count", 9999) < 500 and f.get("impressions", 0) > 5000,
    "ORPHAN_PAGE_FLAG": lambda f: f.get("internal_link_count", 10) < 2 and f.get("impressions", 0) > 1000,
    "RICH_RESULT_OPPORTUNITY": lambda f: f.get("serp_feature_present", 0) == 0 and f.get("position", 100) < 5,
    "CTR_DECAYING": lambda f: f.get("ctr_trend_7d", 0) < -0.005,
    "TRAFFIC_ACCELERATING": lambda f: f.get("click_growth_rate", 0) > 0.3,
}


def validate_search_console_csv(filepath: str) -> ValidationResult:
    import pandas as pd

    result = ValidationResult(is_valid=True)

    try:
        df = pd.read_csv(filepath, nrows=5)
    except FileNotFoundError:
        result.is_valid = False
        result.errors.append(f"File not found: {filepath}")
        return result
    except Exception as e:
        result.is_valid = False
        result.errors.append(f"Failed to read CSV: {e}")
        return result

    required_columns = {"date", "page", "impressions", "clicks", "ctr", "position", "site"}
    missing = required_columns - set(df.columns)
    if missing:
        result.is_valid = False
        result.errors.append(f"Missing required columns: {missing}")

    if result.is_valid and len(df) == 0:
        result.warnings.append("CSV file is empty")

    return result


def quarantined_rows_from_validation(filepath: str) -> list[int]:
    import pandas as pd

    df = pd.read_csv(filepath)
    quarantined = []

    for idx, row in df.iterrows():
        if pd.isna(row.get("ctr")) or row.get("ctr", 0) < 0 or row.get("ctr", 0) > 100:
            quarantined.append(idx)
        if pd.isna(row.get("position")) or row.get("position", 0) <= 0:
            quarantined.append(idx)
        if pd.isna(row.get("impressions")) or row.get("impressions", 0) < 0:
            quarantined.append(idx)
        if pd.isna(row.get("clicks")) or row.get("clicks", 0) < 0:
            quarantined.append(idx)
        if pd.isna(row.get("page")) or str(row.get("page", "")).strip() == "":
            quarantined.append(idx)

    return quarantined
