import pytest
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_search_data():
    dates = pd.date_range("2025-01-01", periods=90, freq="D")
    pages = [f"/page-{i:03d}" for i in range(100)]

    records = []
    for page in pages:
        for date in dates[:30]:
            impressions = np.random.randint(10, 5000)
            ctr = np.random.uniform(0.5, 8.0)
            clicks = max(0, int(impressions * ctr / 100))
            position = np.random.uniform(1, 50)

            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "page": page,
                "site": "example.com",
                "impressions": impressions,
                "clicks": clicks,
                "ctr": round(ctr, 4),
                "position": round(position, 2),
            })

    df = pd.DataFrame(records)
    return df


@pytest.fixture
def sample_feature_columns():
    from src.features.sql_generator import FEATURE_COLUMNS
    return FEATURE_COLUMNS


@pytest.fixture
def sample_page_meta():
    return pd.DataFrame({
        "page": [f"/page-{i:03d}" for i in range(100)],
        "url": [f"https://example.com/page-{i:03d}" for i in range(100)],
        "title_length": np.random.randint(20, 80, 100),
        "word_count": np.random.randint(100, 5000, 100),
        "content_freshness_days": np.random.randint(1, 700, 100),
        "internal_link_count": np.random.randint(0, 20, 100),
    })
