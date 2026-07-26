from __future__ import annotations

import shap
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from src.utils.logging import get_logger

logger = get_logger(__name__)


class SHAPExplainer:
    def __init__(self, model_path: str | None = None, model_dict: dict | None = None):
        self.models = model_dict or {}

        if model_path and not self.models:
            path = Path(model_path)
            if path.exists():
                loaded = joblib.load(str(path))
                if isinstance(loaded, dict):
                    self.models = loaded
                else:
                    self.models = {"default": loaded}

        self.explainers = {}
        for action, model in self.models.items():
            if hasattr(model, "get_booster"):
                self.explainers[action] = shap.TreeExplainer(model)
            elif hasattr(model, "estimators_"):
                self.explainers[action] = shap.TreeExplainer(model)

        logger.info(f"SHAPExplainer initialized with {len(self.explainers)} explainers")

    def explain_prediction(
        self, feature_names: list[str], feature_values: np.ndarray, action: str = "protect"
    ) -> dict:
        explainer = self.explainers.get(action)
        if explainer is None:
            return {"action": action, "error": "No explainer available for this action"}

        shap_values = explainer.shap_values(feature_values.reshape(1, -1))
        base_value = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, np.ndarray)) else explainer.expected_value

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_df = pd.DataFrame({
            "feature": feature_names,
            "shap_value": shap_values.flatten(),
        }).sort_values("shap_value", key=abs, ascending=False)

        return {
            "action": action,
            "base_value": float(base_value),
            "top_contributions": shap_df.head(10).to_dict("records"),
        }

    def global_importance(self, action: str, X: pd.DataFrame) -> pd.DataFrame:
        explainer = self.explainers.get(action)
        if explainer is None:
            return pd.DataFrame()

        shap_values = explainer.shap_values(X.values)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        importance_df = pd.DataFrame({
            "feature": X.columns,
            "mean_abs_shap": mean_abs_shap,
        }).sort_values("mean_abs_shap", ascending=False)

        return importance_df
