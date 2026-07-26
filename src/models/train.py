from __future__ import annotations

from pathlib import Path
import joblib
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, classification_report

from src.utils.logging import get_logger
from src.utils.config import settings
from src.features.sql_generator import FEATURE_COLUMNS

logger = get_logger(__name__)

ACTION_CLASSES = ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]


def generate_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Generate action labels via weak supervision (documented heuristic rules).
    
    These are expert-generated recommendation labels, NOT ground truth labels.
    They represent what an SEO specialist would recommend based on search performance data.
    """
    labels = pd.DataFrame(index=df.index)
    for action in ACTION_CLASSES:
        labels[action] = 0

    # Protect: high CTR, good position, high traffic
    mask = (df["ctr"] > 5) & (df["position"] <= 5) & (df["impressions"] > 1000)
    labels.loc[mask, "protect"] = 1

    # Improve: decent CTR or position but room for optimization
    mask = ((df["position"] < 10) & (df["ctr"] < 3)) | ((df["ctr"] > 2) & (df["position"] > 10))
    labels.loc[mask, "improve"] = 1

    # Refresh: moderate performance with stale content
    mask = (df["ctr"] > 2) & (df["ctr"] < 6) & (df["position"] > 10) & (df["position"] < 30)
    labels.loc[mask, "refresh"] = 1

    # Rewrite: poor overall performance, high potential impact
    mask = (df["position"] > 20) & (df["impressions"] > 500) & (df["ctr"] < 2)
    labels.loc[mask, "rewrite"] = 1

    # Merge: cannibalization detected
    mask = df.get("cannibalization_flag", pd.Series(0, index=df.index)) > 1
    labels.loc[mask, "merge"] = 1

    # Prune: very low CTR, low position, low impressions
    mask = (df["ctr"] < 0.5) & (df["position"] > 20) & (df["impressions"] < 500)
    labels.loc[mask, "prune"] = 1

    # Monitor: everything else (stable but low value)
    mask = labels.sum(axis=1) == 0
    labels.loc[mask, "monitor"] = 1

    return labels


def train(models_dir: str = None) -> dict:
    models_dir = Path(models_dir) if models_dir else Path(settings.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting XGBoost training pipeline")

    feature_path = settings.processed_dir / "features.parquet"
    if not feature_path.exists():
        logger.error(f"Feature matrix not found: {feature_path}")
        return {}

    df = pd.read_parquet(str(feature_path))
    logger.info(f"Loaded feature matrix: {len(df)} rows, {len(df.columns)} columns")

    feature_cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    if len(feature_cols) < 5:
        logger.warning(f"Only {len(feature_cols)} features available")

    labels_df = generate_labels(df)

    split_idx = int(len(df) * 0.75)
    X_train = df[feature_cols].iloc[:split_idx].fillna(0).replace([np.inf, -np.inf], 0).values
    X_test = df[feature_cols].iloc[split_idx:].fillna(0).replace([np.inf, -np.inf], 0).values
    y_train = labels_df.iloc[:split_idx]
    y_test = labels_df.iloc[split_idx:]

    logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

    models = {}
    all_metrics = {}

    for action in ACTION_CLASSES:
        y_tr = y_train[action].values.astype(float)
        y_te = y_test[action].values.astype(float)
        pos = y_tr.sum()

        if pos < 10 or pos > len(y_tr) * 0.95:
            logger.info(f"  {action}: skipped ({pos} positive examples)")
            continue

        scale_pos_weight = min((len(y_tr) - pos) / max(pos, 1), 10.0)
        dtrain = xgb.DMatrix(X_train, label=y_tr)
        dtest = xgb.DMatrix(X_test, label=y_te)

        params = {
            "objective": "binary:logistic",
            "eval_metric": "auc",
            "max_depth": 6,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "scale_pos_weight": scale_pos_weight,
            "tree_method": "hist",
            "random_state": 42,
            "n_jobs": -1,
            "verbosity": 0,
        }

        model = xgb.train(
            params, dtrain, num_boost_round=200,
            evals=[(dtest, "test")], verbose_eval=False,
        )

        y_proba = model.predict(dtest)
        y_pred = (y_proba >= 0.5).astype(int)

        auc = roc_auc_score(y_te, y_proba) if len(np.unique(y_te)) > 1 else 0.0
        f1 = f1_score(y_te, y_pred, zero_division=0)
        prec = precision_score(y_te, y_pred, zero_division=0)
        rec = recall_score(y_te, y_pred, zero_division=0)

        models[action] = model
        all_metrics[action] = {
            "auc": round(auc, 4),
            "f1": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "pos_count": int(pos),
            "neg_count": int(len(y_tr) - pos),
        }
        logger.info(f"  {action}: AUC={auc:.4f} F1={f1:.4f}")

    macro_auc = np.mean([m["auc"] for m in all_metrics.values()])
    macro_f1 = np.mean([m["f1"] for m in all_metrics.values()])
    logger.info(f"Macro AUC: {macro_auc:.4f}, Macro F1: {macro_f1:.4f}")

    joblib.dump(
        {"models": models, "metrics": all_metrics, "feature_cols": feature_cols, "macro_auc": macro_auc, "macro_f1": macro_f1},
        str(models_dir / "xgboost_model.joblib"),
    )
    with open(models_dir / "metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)

    logger.info(f"Models saved to {models_dir / 'xgboost_model.joblib'}")
    return {"models": models, "metrics": all_metrics, "macro_auc": macro_auc, "macro_f1": macro_f1}
