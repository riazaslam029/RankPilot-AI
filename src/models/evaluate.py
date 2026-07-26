from __future__ import annotations

import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from src.utils.logging import get_logger
from src.utils.config import settings

logger = get_logger(__name__)

ACTION_CLASSES = ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]


def evaluate_model(models: dict, X_test: pd.DataFrame, y_test: pd.DataFrame) -> dict:
    results = {}

    for action in ACTION_CLASSES:
        model = models.get(action)
        if model is None:
            continue

        y_true = y_test[action]
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
            y_pred = model.predict(X_test)
        except Exception as e:
            logger.warning(f"Prediction failed for {action}: {e}")
            continue

        if len(np.unique(y_true)) < 2:
            logger.warning(f"Single class in test set for {action}; skipping AUC")
            auc = None
        else:
            auc = roc_auc_score(y_true, y_proba)

        results[action] = {
            "auc": auc,
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "support": int(y_true.sum()),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        }

        logger.info(f"{action}: AUC={auc:.4f if auc else 'N/A'}, F1={results[action]['f1']:.4f}")

    return results


def plot_roc_curves(models: dict, X_test: pd.DataFrame, y_test: pd.DataFrame, output_path: str) -> str:
    fig = go.Figure()
    colors = px.colors.qualitative.Plotly

    for idx, action in enumerate(ACTION_CLASSES):
        model = models.get(action)
        if model is None:
            continue

        try:
            y_proba = model.predict_proba(X_test)[:, 1]
            y_true = y_test[action]

            if len(np.unique(y_true)) < 2:
                continue

            from sklearn.metrics import roc_curve
            fpr, tpr, _ = roc_curve(y_true, y_proba)
            auc = roc_auc_score(y_true, y_proba)

            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines", name=f"{action} (AUC={auc:.3f})",
                line=dict(color=colors[idx % len(colors)], width=2),
            ))
        except Exception:
            continue

    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines", name="Random",
        line=dict(dash="dash", color="gray"),
    ))

    fig.update_layout(
        title="ROC Curves by Action Class",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=600,
        legend=dict(x=0.7, y=0.05),
    )

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out))
    return str(out)


def plot_feature_importance(shap_values: np.ndarray, feature_names: list[str], output_path: str) -> str:
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_idx = np.argsort(mean_abs_shap)[-20:]

    fig = px.bar(
        x=mean_abs_shap[top_idx],
        y=[feature_names[i] for i in top_idx],
        orientation="h",
        title="Top 20 Features by Mean |SHAP Value|",
        labels={"x": "Mean |SHAP Value|", "y": "Feature"},
    )
    fig.update_layout(height=600)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(out))
    return str(out)


def save_evaluation_report(results: dict, output_path: str) -> str:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "model_type": "XGBoost multi-label classifier",
        "num_actions": len(results),
        "metrics_by_action": results,
        "macro_f1": np.mean([r["f1"] for r in results.values() if isinstance(r, dict)]),
        "macro_auc": np.mean([r["auc"] for r in results.values() if isinstance(r, dict) and r.get("auc") is not None]),
    }

    with open(str(out), "w") as f:
        json.dump(report, f, indent=2, default=str)

    return str(out)
