from __future__ import annotations

REASON_CODES = {
    "HIGH_TRAFFIC_IMPACT": {
        "condition": "impressions > 95th percentile",
        "meaning": "Page has significant traffic at stake",
        "action": "Investigate and optimize this high-value page",
        "weight": 1.0,
    },
    "CTR_BELOW_THRESHOLD": {
        "condition": "ctr < 0.01 AND position < 10",
        "meaning": "Page ranks well but fails to attract clicks",
        "action": "Optimize title tag and meta description for CTR improvement",
        "weight": 0.9,
    },
    "CTR_WELL_ABOVE_AVG": {
        "condition": "ctr > 90th percentile for position bucket",
        "meaning": "Page outperforms competitors at this rank",
        "action": "Protect this page from changes; monitor for fluctuations",
        "weight": 0.8,
    },
    "POSITION_DECLINING": {
        "condition": "position_trend_7d < -1.0 AND position > 10",
        "meaning": "Page is losing rankings rapidly",
        "action": "Investigate ranking decline: check new competitors, technical issues, content freshness",
        "weight": 0.9,
    },
    "POSITION_IMPROVING": {
        "condition": "position_trend_7d > 1.0 AND position < 20",
        "meaning": "Page is gaining rankings momentum",
        "action": "Protect momentum; consider adding internal links to reinforce",
        "weight": 0.7,
    },
    "CONTENT_STALE": {
        "condition": "content_freshness_days > 365",
        "meaning": "Content has not been updated in over a year",
        "action": "Update content with current data, refresh statistics, update outbound links",
        "weight": 0.6,
    },
    "TITLE_OPTIMIZATION": {
        "condition": "title_length > 70 OR title_length < 30",
        "meaning": "Title tag length is suboptimal for SERP display",
        "action": "Revise title tag to 50-60 characters with primary keyword near the front",
        "weight": 0.5,
    },
    "META_DESC_OPTIMIZATION": {
        "condition": "meta_desc_length > 170 OR meta_desc_length < 50",
        "meaning": "Meta description length is suboptimal",
        "action": "Rewrite meta description to 150-160 characters with compelling call to action",
        "weight": 0.4,
    },
    "LOW_INTERNAL_LINKS": {
        "condition": "internal_link_count < 3",
        "meaning": "Page has insufficient internal link support",
        "action": "Add contextual internal links from related pages to improve crawl budget",
        "weight": 0.5,
    },
    "HIGH_CANNIBALIZATION": {
        "condition": "cannibalization_flag > 2",
        "meaning": "Multiple pages compete for the same queries",
        "action": "Consider consolidating overlapping pages to avoid self-cannibalization",
        "weight": 0.7,
    },
    "ORPHAN_PAGE_FLAG": {
        "condition": "internal_link_count < 2 AND impressions > 1000",
        "meaning": "High-traffic page is orphaned with few internal links",
        "action": "Add contextual internal links from high-authority pages",
        "weight": 0.6,
    },
    "RICH_RESULT_OPPORTUNITY": {
        "condition": "serp_feature_present == 0 AND position < 5",
        "meaning": "Page ranks well but misses SERP feature opportunities",
        "action": "Implement structured data (FAQ, HowTo, Article schema) to qualify for rich results",
        "weight": 0.8,
    },
    "CTR_DECAYING": {
        "condition": "ctr_trend_7d < -0.005",
        "meaning": "CTR is declining day over day",
        "action": "Investigate CTR decline; check for title truncation, content quality, or competitor changes",
        "weight": 0.7,
    },
    "TRAFFIC_ACCELERATING": {
        "condition": "click_growth_rate > 0.3",
        "meaning": "Page is growing traffic rapidly",
        "action": "Protect and amplify this growing page; ensure infrastructure can handle load",
        "weight": 0.8,
    },
}


def generate_reason_codes(features: dict) -> list[str]:
    matched = []
    for code, info in REASON_CODES.items():
        try:
            if evaluate_condition(info["condition"], features):
                matched.append(code)
        except Exception:
            continue

    matched.sort(key=lambda c: REASON_CODES[c]["weight"], reverse=True)
    return matched[:5]


def evaluate_condition(condition: str, features: dict) -> bool:
    import numpy as np

    safe_features = {}
    for k, v in features.items():
        try:
            safe_features[k] = float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0.0
        except (TypeError, ValueError):
            safe_features[k] = 0.0

    condition_lower = condition.lower()

    if "impressions >" in condition_lower and "percentile" in condition_lower:
        return safe_features.get("impressions", 0) > 0
    if "ctr <" in condition_lower and "position <" in condition_lower:
        return safe_features.get("ctr", 0) < 0.01 and safe_features.get("position", 0) < 10
    if "ctr >" in condition_lower and "percentile" in condition_lower and "position" in condition_lower:
        return safe_features.get("ctr", 0) > 0.05 and safe_features.get("position", 0) <= 5
    if "position_trend_7d" in condition_lower and "position >" in condition_lower:
        return safe_features.get("position_trend_7d", 0) < -1.0 and safe_features.get("position", 0) > 10
    if "position_trend_7d" in condition_lower and "position <" in condition_lower:
        return safe_features.get("position_trend_7d", 0) > 1.0 and safe_features.get("position", 0) < 20
    if "content_freshness_days" in condition_lower and "> 365" in condition_lower:
        return safe_features.get("content_freshness_days", 999) > 365
    if "content_freshness_days" in condition_lower and "< 30" in condition_lower:
        return safe_features.get("content_freshness_days", 0) < 30
    if "title_length" in condition_lower:
        tl = safe_features.get("title_length", 0)
        return tl > 70 or tl < 30
    if "meta_desc_length" in condition_lower:
        ml = safe_features.get("meta_desc_length", 0)
        return ml > 170 or ml < 50
    if "internal_link_count" in condition_lower and "< 3" in condition_lower:
        return safe_features.get("internal_link_count", 10) < 3
    if "cannibalization_flag" in condition_lower and "> 2" in condition_lower:
        return safe_features.get("cannibalization_flag", 0) > 2
    if "word_count" in condition_lower and "impressions" in condition_lower:
        return safe_features.get("word_count", 9999) < 500 and safe_features.get("impressions", 0) > 5000
    if "internal_link_count" in condition_lower and "< 2" in condition_lower:
        return safe_features.get("internal_link_count", 10) < 2 and safe_features.get("impressions", 0) > 1000
    if "serp_feature_present" in condition_lower and "position <" in condition_lower:
        return safe_features.get("serp_feature_present", 0) == 0 and safe_features.get("position", 100) < 5
    if "ctr_trend" in condition_lower and "< -0.005" in condition_lower:
        return safe_features.get("ctr_trend_7d", 0) < -0.005
    if "click_growth_rate" in condition_lower and "> 0.3" in condition_lower:
        return safe_features.get("click_growth_rate", 0) > 0.3
    return False
