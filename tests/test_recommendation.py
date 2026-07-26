import pytest
import pandas as pd
import numpy as np

from src.recommendation.scoring import (
    compute_priority_score,
    get_priority_tier,
    compute_business_impact,
    ACTION_CLASSES,
    PRIORITY_THRESHOLD,
)
from src.recommendation.reason_codes import generate_reason_codes, REASON_CODES


@pytest.fixture
def sample_features():
    return {
        "impressions": 50000,
        "ctr": 2.0,
        "position": 15.0,
        "ctr_trend_7d": -0.015,
        "position_trend_7d": -2.5,
        "content_freshness_days": 400,
        "click_growth_rate": 0.1,
        "internal_link_count": 2,
        "word_count": 300,
        "title_length": 75,
    }


def test_compute_priority_score(sample_features):
    action_scores = {"protect": 0.8, "improve": 0.5, "refresh": 0.3, "prune": 0.1}
    score = compute_priority_score(action_scores, confidence=0.9, features=sample_features)
    assert 0 <= score <= 100


def test_get_priority_tier():
    assert get_priority_tier(90) == "critical"
    assert get_priority_tier(75) == "high"
    assert get_priority_tier(50) == "medium"
    assert get_priority_tier(30) == "low"
    assert get_priority_tier(10) == "monitor"


def test_compute_business_impact():
    result = compute_business_impact(impressions=10000, potential_ctr_gain=2.0)
    assert isinstance(result, float)
    assert result >= 0


def test_generate_reason_codes(sample_features):
    codes = generate_reason_codes(sample_features)
    assert isinstance(codes, list)
    assert len(codes) <= 5


def test_reason_codes_dict_complete():
    known_codes = list(REASON_CODES.keys())
    assert len(known_codes) >= 10

    for code, info in REASON_CODES.items():
        assert "condition" in info
        assert "meaning" in info
        assert "action" in info
        assert "weight" in info
        assert info["weight"] > 0
