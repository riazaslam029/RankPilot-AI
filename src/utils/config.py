import os
from pathlib import Path


class Settings:
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = project_root / "data"
    raw_dir: Path = data_dir / "raw"
    processed_dir: Path = data_dir / "processed"
    models_dir: Path = project_root / "models"
    configs_dir: Path = project_root / "configs"
    notebook_dir: Path = project_root / "notebooks"
    tests_dir: Path = project_root / "tests"
    submission_dir: Path = project_root / "submission"

    duckdb_path: Path = processed_dir / "analytics.duckdb"
    mlflow_tracking_uri: str = "file:./mlruns"
    model_version: str = "v1.0.0"

    api_host: str = os.environ.get("API_HOST", "0.0.0.0")
    api_port: int = int(os.environ.get("API_PORT", "8000"))
    streamlit_port: int = int(os.environ.get("STREAMLIT_PORT", "8501"))

    default_date_start: str = "2025-01-01"
    default_date_end: str = "2026-07-25"


settings = Settings()
