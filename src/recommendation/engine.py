from __future__ import annotations

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

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
        self.model_path = model_path or str(settings.models_dir / "xgboost_model.joblib")
        self.models = self._load_models()
        logger.info(f"RecommendationEngine initialized with {len(self.models)} action models")

    def _load_models(self) -> dict:
        path = Path(self.model_path)
        if not path.exists():
            logger.warning(f"Model not found at {path}; using uninitialized state")
            return {}
        loaded = joblib.load(str(path))
        if isinstance(loaded, dict):
            return loaded
        return {"default": loaded}

    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        results = []

        for _, row in features_df.iterrows():
            feature_dict = row.to_dict()
            action_scores = {}
            action_probs = {}
            reason_codes_list = []

            for action in ACTION_CLASSES:
                model = self.models.get(action)
                if model is None:
                    action_scores[action] = 0.0
                    action_probs[action] = 0.0
                    continue

                try:
                    feature_array = np.array(
                        [[row.get(f, 0.0) for f in row.index if f != "page" and f != "date"]]
                    )
                    prob = model.predict_proba(feature_array)[0][1] if hasattr(model, "predict_proba") else 0.5
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
            primary_score = action_scores.get(primary_action, 0.0)
            confidence = max(action_probs.values()) if action_probs else 0.0
            priority = compute_priority_score(action_scores, confidence, feature_dict)
            tier = get_priority_tier(priority)

            estimated_impact = compute_business_impact(
                impressions=feature_dict.get("impressions", 0),
                potential_ctr_gain=feature_dict.get("ctr", 0) * 100,
            )

            results.append({
                "page": feature_dict.get("page", ""),
                "primary_action": primary_action,
                "all_scores": {a: action_scores.get(a, 0.0) for a in ACTION_CLASSES},
                "all_probs": {a: round(action_probs.get(a, 0.0), 4) for a in ACTION_CLASSES},
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
        for code in reason_codes[:3]:
            action_map = {
                "CTR_BELOW_THRESHOLD": "Optimize title tag and meta description to increase CTR",
                "POSITION_DECLINING": "Investigate ranking decline; check technical SEO and content freshness",
                "CONTENT_STALE": "Update content to reflect current information and data",
                "TITLE_OPTIMIZATION": "Revise title tag to 50-60 characters with primary keyword",
                "HIGH_CANNIBALIZATION": "Consider merging with overlapping pages to avoid self-cannibalization",
                "HIGH_BROWSE_DEPTH_NEEDED": "Expand content depth with additional sections and data",
                "ORPHAN_PAGE_FLAG": "Add contextual internal links from related pages",
                "RICH_RESULT_OPPORTUNITY": "Implement structured data (FAQ, HowTo schema) for rich results",
                "CTR_DECAYING": "Investigate CTR decline; check title truncation and competitor changes",
                "TRAFFIC_ACCELERATING": "Protect and amplify this growing page",
                "HIGH_TRAFFIC_IMPACT": "This high-traffic page needs action; review its current performance",
                "CTR_WELL_ABOVE_AVG": "Protect this high-performing page; monitor for changes",
                "POSITION_IMPROVING": "Protect momentum; add internal links to reinforce gains",
            }
            action = action_map.get(code, f"Review page for {code.replace('_', ' ').lower()}")
            actions.append(action)
        return actions


def run_recommendation(input_path: str, output_path: str) -> str:
    logger.info("Running recommendation engine")

    features_df = pd.read_parquet(input_path) if input_path.endswith(".parquet") else pd.read_csv(input_path)
    logger.info(f"Loaded {len(features_df)} rows for recommendations")

    engine = RecommendationEngine()
    results = engine.predict(features_df)

    results = results.sort_values("priority_score", ascending=False).reset_index(drop=True)
    results["priority_rank"] = range(1, len(results) + 1)

    results["reason_codes"] = results["reason_codes"].apply(lambda x: json.dumps(x))
    results["all_scores"] = results["all_scores"].apply(json.dumps)
    results["all_probs"] = results["all_probs"].apply(json.dumps)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(str(output), index=False)

    logger.info(f"Recommendations complete: {len(results)} pages analyzed")
    logger.info(f"Top action distribution: {results['primary_action'].value_counts().to_dict()}")
    logger.info(f"Top opportunities (critical): {len(results[results['priority_tier'] == 'critical'])} pages")

    return str(output)
