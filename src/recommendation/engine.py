from __future__ import annotations

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

import joblib

from src.utils.logging import get_logger
from src.utils.config import settings
from src.recommendation.scoring import (
    compute_priority_score,
    get_priority_tier,
    compute_business_impact,
    ACTION_CLASSES,
    ACTION_WEIGHTS,
)
from src.recommendation.reason_codes import generate_reason_codes

logger = get_logger(__name__)


class RecommendationEngine:
    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or str(settings.models_dir / "checkpoints" / "xgboost_model.joblib")
        self.models: dict = {}
        self.metrics: dict = {}
        self.feature_cols: list[str] = []
        self._load_models()

    def _load_models(self) -> None:
        path = Path(self.model_path)
        if not path.exists():
            logger.warning(f"Model not found at {path}; using fallback mode")
            return
        data = joblib.load(str(path))
        if isinstance(data, dict):
            self.models = data.get("models", {})
            self.metrics = data.get("metrics", {})
            self.feature_cols = data.get("feature_cols", [])
            logger.info(f"Loaded {len(self.models)} models with {len(self.feature_cols)} features")
        else:
            logger.warning("Unexpected model format")

    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        results = []
        feature_cols = self.feature_cols or [c for c in features_df.columns if c not in ("page", "date", "site")]

        for idx, row in features_df.iterrows():
            feature_dict = row.to_dict()
            action_scores = {}
            action_probs = {}

            for action in ACTION_CLASSES:
                model = self.models.get(action)
                if model is None:
                    action_scores[action] = 0.0
                    action_probs[action] = 0.0
                    continue

                try:
                    vals = [row.get(c, 0.0) for c in feature_cols]
                    vals = np.array(vals).reshape(1, -1)
                    vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
                    prob = model.predict(vals)[0]
                except Exception:
                    prob = 0.1

                action_probs[action] = float(prob)
                weighted_score = float(prob * ACTION_WEIGHTS.get(action, 0.5))
                action_scores[action] = round(weighted_score, 2)

            try:
                reason_codes_list = generate_reason_codes(feature_dict)
            except Exception:
                reason_codes_list = []

            primary_action = max(action_scores, key=action_scores.get) if action_scores else "monitor"
            confidence = max(action_probs.values()) if action_probs else 0.0
            priority = compute_priority_score(action_scores, confidence, feature_dict)
            tier = get_priority_tier(priority)
            estimated_impact = compute_business_impact(
                impressions=feature_dict.get("impressions", 0),
                potential_ctr_gain=feature_dict.get("ctr", 0) * 100,
            )

            results.append({
                "page": feature_dict.get("page", f"page-{idx}"),
                "primary_action": primary_action,
                "all_scores": action_scores,
                "all_probs": {a: round(p, 4) for a, p in action_probs.items()},
                "confidence": round(confidence, 4),
                "priority_score": priority,
                "priority_tier": tier,
                "reason_codes": reason_codes_list,
                "suggested_actions": self._generate_suggested_actions(reason_codes_list, feature_dict),
                "estimated_monthly_impact_usd": estimated_impact,
            })

        return pd.DataFrame(results)

    def _generate_suggested_actions(self, reason_codes: list[str], features: dict) -> list[str]:
        actions = []
        templates = {
            "CTR_BELOW_THRESHOLD": f"Optimize title tag and meta description. Current CTR is {features.get('ctr', 0):.2f}% at position {features.get('position', 0):.0f}.",
            "POSITION_DECLINING": "Investigate ranking decline. Check for new competitors, technical SEO issues, and content freshness.",
            "CONTENT_STALE": f"Update content. Last updated {features.get('content_freshness_days', 0)} days ago.",
            "TITLE_OPTIMIZATION": f"Revise title tag. Current length: {features.get('title_length', 0)} chars.",
            "HIGH_CANNIBALIZATION": "Consider merging to avoid keyword cannibalization.",
            "HIGH_BROWSE_DEPTH_NEEDED": "Expand content depth — page may be too thin for its traffic.",
            "ORPHAN_PAGE_FLAG": "Add internal links from related pages to improve crawl budget.",
            "RICH_RESULT_OPPORTUNITY": "Implement structured data (FAQ, HowTo schema) for rich results potential.",
            "CTR_DECAYING": "Investigate CTR decline. Check title truncation and competitor changes.",
            "TRAFFIC_ACCELERATING": "Protect and amplify this growing page.",
            "HIGH_TRAFFIC_IMPACT": "This high-traffic page needs attention.",
            "CTR_WELL_ABOVE_AVG": "Protect this high-performing page.",
            "POSITION_IMPROVING": "Protect momentum. Add internal links to reinforce gains.",
        }
        for code in reason_codes[:3]:
            action = templates.get(code, f"Review page for {code.replace('_', ' ').lower()}")
            actions.append(action)
        return actions


def run_recommendation(input_path: str, output_path: str) -> str:
    logger.info("Running recommendation engine")
    features_df = pd.read_parquet(input_path) if input_path.endswith(".parquet") else pd.read_csv(input_path)
    logger.info(f"Loaded {len(features_df)} rows")
    engine = RecommendationEngine()
    results = engine.predict(features_df)
    results = results.sort_values("priority_score", ascending=False).reset_index(drop=True)
    results["priority_rank"] = range(1, len(results) + 1)
    for col in ["all_scores", "reason_codes"]:
        results[col] = results[col].apply(json.dumps)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(str(output), index=False)
    logger.info(f"Recommendations saved: {len(results)} pages")
    return str(output)
