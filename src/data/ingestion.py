from __future__ import annotations

import pandas as pd
from pathlib import Path

from src.utils.logging import get_logger
from src.utils.config import settings

logger = get_logger(__name__)

REQUIRED_COLUMNS = {"date", "page", "impressions", "clicks", "ctr", "position", "site"}


def ingest_csv(filepath: str) -> pd.DataFrame:
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    logger.info(f"Reading CSV: {filepath}")
    df = pd.read_csv(filepath)

    if df.empty:
        raise ValueError("Input CSV is empty")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["page"] = df["page"].astype(str).str.strip()
    df["site"] = df["site"].astype(str).str.strip()
    df["ctr"] = pd.to_numeric(df["ctr"], errors="coerce").fillna(0.0)
    df["position"] = pd.to_numeric(df["position"], errors="coerce").fillna(100.0)
    df["impressions"] = pd.to_numeric(df["impressions"], errors="coerce").fillna(0).astype(int)
    df["clicks"] = pd.to_numeric(df["clicks"], errors="coerce").fillna(0).astype(int)

    logger.info(f"Ingested {len(df)} rows from {filepath}")
    return df


def ingest_directory(directory: str) -> pd.DataFrame:
    dirpath = Path(directory)
    if not dirpath.exists():
        raise FileNotFoundError(f"Directory not found: {dirpath}")

    csv_files = list(dirpath.glob("*.csv")) + list(dirpath.glob("*.csv.gz"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {dirpath}")

    frames = []
    for f in csv_files:
        try:
            df = ingest_csv(str(f))
            frames.append(df)
        except Exception as e:
            logger.warning(f"Skipping {f}: {e}")

    if not frames:
        raise ValueError("No valid CSV files could be ingested")

    combined = pd.concat(frames, ignore_index=True)
    logger.info(f"Combined {len(frames)} files into {len(combined)} rows")
    return combined


def save_parquet(df: pd.DataFrame, filepath: str) -> None:
    out = Path(filepath)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(str(out), index=False, compression="snappy")
    logger.info(f"Saved {len(df)} rows to {out}")


def load_parquet(filepath: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")

    df = pd.read_parquet(str(path))
    logger.info(f"Loaded {len(df)} rows from {path}")
    return df


def prepare_for_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["page", "date"]).reset_index(drop=True)
    df["day_of_week"] = df["date"].dt.dayofweek
    df = df[df["impressions"] > 0].reset_index(drop=True)
    logger.info(f"Prepared {len(df)} rows for feature engineering")
    return df
