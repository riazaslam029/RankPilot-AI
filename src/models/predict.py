from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.config import settings

logger = get_logger(__name__)


def predict(features_df: pd.DataFrame, model_path: str | None = None) -> pd.DataFrame:
    path = model_path or str(settings.models_dir / "xgboost_model.joblib")
    models = joblib.load(path) if Path(path).exists() else {}

    if isinstance(models, dict) and not models:
        logger.warning("No models loaded; returning empty predictions")
        return pd.DataFrame(columns=["page"] + [f"{a}_score" for a in ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]])

    results = {"page": features_df["page"] if "page" in features_df.columns else features_df.index}

    feature_cols = [c for c in features_df.columns if c not in ["page", "date"]]

    for action in ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]:
        model = models.get(action) if isinstance(models, dict) else None
        if model is not None and hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(features_df[feature_cols])[:, 1]
                results[f"{action}_score"] = probs
            except Exception as e:
                logger.warning(f"Prediction failed for {action}: {e}")
                results[f"{action}_score"] = 0.0
        else:
            results[f"{action}_score"] = 0.0

    return pd.DataFrame(results)
