from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.config import settings
from src.features.sql_generator import FEATURE_COLUMNS

logger = get_logger(__name__)

ACTION_CLASSES = ["protect", "improve", "refresh", "rewrite", "merge", "prune", "monitor"]


def generate_labels(df: pd.DataFrame) -> pd.DataFrame:
    labels = pd.DataFrame(index=df.index)
    for action in ACTION_CLASSES:
        labels[action] = 0

    mask = (df["ctr"] < 0.01) & (df["position"] > 20)
    labels.loc[mask, "prune"] = 1

    mask = (df["ctr"] > 10) & (df["position"] < 5)
    labels.loc[mask, "protect"] = 1

    mask = (df["position"] < 5) & (df["ctr"] < 5)
    labels.loc[mask, "improve"] = 1

    mask = (df["ctr"] > 5) & (df["position"] > 10)
    labels.loc[mask, "improve"] = 1

    mask = (df["ctr"] > 5) & (df["position"] > 15)
    labels.loc[mask, "refresh"] = 1

    mask = (df["position"] > 30) & (df["impressions"] > 1000)
    labels.loc[mask, "rewrite"] = 1

    mask = (df["ctr"] < 0.5) & (df["position"] > 10) & (df["impressions"] > 500)
    mask &= labels[["protect", "improve", "refresh", "rewrite", "prune"]].sum(axis=1) == 0
    labels.loc[mask, "monitor"] = 1

    mask = labels.sum(axis=1) == 0
    labels.loc[mask, "monitor"] = 1

    return labels


def train_single_classifier(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    label: str,
) -> tuple[xgb.XGBClassifier, dict]:
    params = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": 6,
        "learning_rate": 0.05,
        "n_estimators": 500,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "tree_method": "hist",
        "random_state": 42,
        "n_jobs": -1,
        "use_label_encoder": False,
    }

    model = xgb.XGBClassifier(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    y_pred = model.predict_proba(X_val)[:, 1]
    y_pred_class = model.predict(X_val)

    metrics = {
        "label": label,
        "auc": roc_auc_score(y_val, y_pred),
        "f1": f1_score(y_val, y_pred_class, zero_division=0),
        "precision": 0.0,
        "recall": 0.0,
    }
    if sum(y_val) > 0 and sum(y_pred_class) > 0:
        precision = sum((y_pred_class == 1) & (y_val == 1)) / sum(y_pred_class == 1)
        recall = sum((y_pred_class == 1) & (y_val == 1)) / max(sum(y_val == 1), 1)
        metrics["precision"] = precision
        metrics["recall"] = recall

    logger.info(f"  {label}: AUC={metrics['auc']:.4f}, F1={metrics['f1']:.4f}")

    return model, metrics


def train(models_dir: str = None) -> dict:
    models_dir = Path(models_dir or settings.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting model training pipeline")

    feature_path = settings.processed_dir / "features.parquet"
    if not feature_path.exists():
        logger.error(f"Feature matrix not found: {feature_path}")
        logger.info("Run feature engineering pipeline first")
        return {}

    df = pd.read_parquet(str(feature_path))
    logger.info(f"Loaded feature matrix: {len(df)} rows, {len(df.columns)} columns")

    feature_cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    if len(feature_cols) < 10:
        logger.warning(f"Only {len(feature_cols)} features available; expected 52+")

    labels_df = generate_labels(df)

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    labels_df = labels_df.loc[df.index]

    split_idx = int(len(df) * 0.75)
    X_train_val = df[feature_cols].iloc[:split_idx].reset_index(drop=True)
    y_train_val = labels_df.iloc[:split_idx].reset_index(drop=True)
    X_test = df[feature_cols].iloc[split_idx:].reset_index(drop=True)
    y_test = labels_df.iloc[split_idx:].reset_index(drop=True)

    tscv = TimeSeriesSplit(n_splits=5)
    for train_idx, val_idx in tscv.split(X_train_val):
        pass
    X_tr, X_val = X_train_val.iloc[train_idx], X_train_val.iloc[val_idx]
    y_tr, y_val = y_train_val.iloc[train_idx], y_train_val.iloc[val_idx]

    models = {}
    all_metrics = []

    logger.info(f"Training {len(ACTION_CLASSES)} classifiers...")
    for action in ACTION_CLASSES:
        logger.info(f"Training {action} classifier...")
        y_tr_action = y_tr[action]
        y_val_action = y_val[action]

        if y_tr_action.sum() == 0:
            logger.warning(f"No positive examples for {action}; skipping")
            continue

        model, metrics = train_single_classifier(X_tr, y_tr_action, X_val, y_val_action, action)
        models[action] = model
        all_metrics.append(metrics)

    logger.info(f"Trained {len(models)} / {len(ACTION_CLASSES)} classifiers")

    model_path = models_dir / "xgboost_model.joblib"
    joblib.dump(models, str(model_path))
    logger.info(f"Models saved to {model_path}")

    metrics_path = models_dir / "training_metrics.json"
    import json
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)

    return {"models": models, "metrics": all_metrics, "feature_cols": feature_cols}
