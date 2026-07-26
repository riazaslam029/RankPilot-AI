from __future__ import annotations

import numpy as np
from typing import Optional

ACTION_CLASSES = ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]

ACTION_WEIGHTS = {
    "protect": 1.0,
    "improve": 0.9,
    "refresh": 0.7,
    "rewrite": 0.8,
    "merge": 0.5,
    "prune": 0.4,
    "monitor": 0.3,
}

PRIORITY_THRESHOLD = {
    "critical": (85, 100),
    "high": (65, 85),
    "medium": (40, 65),
    "low": (20, 40),
    "monitor": (0, 20),
}


def compute_priority_score(
    action_scores: dict[str, float],
    confidence: float,
    features: Optional[dict] = None,
) -> float:
    if not action_scores:
        return 0.0

    best_score = max(action_scores[a] for a in ACTION_CLASSES if a in action_scores)

    estimated_traffic_impact = 0.0
    if features:
        impressions = features.get("impressions", 0)
        ctr = features.get("ctr", 0) / 100 if features.get("ctr", 0) > 1 else features.get("ctr", 0)
        position = features.get("position", 100)
        est_traffic = impressions * ctr
        potential_gain = max(0, (5.0 - ctr * 100) / 5.0) if ctr < 0.05 else 0.1
        estimated_traffic_impact = min(est_traffic * potential_gain, 1.0)

    urgency = 0.0
    if features:
        ctr_trend = abs(features.get("ctr_trend_7d", 0))
        pos_trend = abs(features.get("position_trend_7d", 0))
        urgency = min(ctr_trend + pos_trend, 2.0) / 2.0

    ease_of_action = 0.5
    if features:
        stale = features.get("content_freshness_days", 365)
        ease_of_action = max(0.1, min(1.0, 1.0 - stale / 730.0))

    priority_score = (
        0.4 * estimated_traffic_impact
        + 0.25 * confidence
        + 0.2 * urgency
        + 0.15 * ease_of_action
    )

    return round(max(0.0, min(100.0, priority_score * 100)), 1)


def get_priority_tier(score: float) -> str:
    if score >= 85:
        return "critical"
    elif score >= 65:
        return "high"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "low"
    else:
        return "monitor"


def compute_business_impact(
    impressions: float,
    potential_ctr_gain: float,
    conversion_rate: float = 0.03,
    avg_revenue_per_conversion: float = 15.0,
) -> float:
    additional_clicks = impressions * (potential_ctr_gain / 100.0)
    additional_conversions = additional_clicks * conversion_rate
    monthly_revenue = additional_conversions * avg_revenue_per_conversion
    return round(monthly_revenue, 2)
