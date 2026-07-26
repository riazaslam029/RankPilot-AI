# RankPilot AI — Search Intelligence Platform

An AI-powered Search Intelligence platform that analyzes search performance data and predicts which pages should be protected, improved, refreshed, rewritten, merged, pruned, or monitored — with explainable recommendations and reason codes.

[![CI Status](https://github.com/username/rankpilot-ai/actions/workflows/CI.yml/badge.svg)](https://github.com/username/rankpilot-ai)
[![Model Version](https://img.shields.io/badge/model-v1.0.0-blue)](https://github.com/username/rankpilot-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What It Does

1. **Ingests** Google Search Console CSV exports (or generates synthetic data for development)
2. **Engineers** 69 features across engagement, temporal, content, competitive, behavioral, and interaction categories
3. **Trains** XGBoost multi-label classifiers that predict 7 action dimensions per page
4. **Generates** explainable recommendations with reason codes, priority tiers, confidence scores, and estimated business impact
5. **Visualizes** everything with an interactive Streamlit dashboard

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic search performance data
python scripts/generate_synthetic_data.py

# Run feature engineering pipeline
python -c "from src.features.pipeline import run_feature_pipeline; run_feature_pipeline('data/raw/search_performance.csv', 'data/processed/features.parquet')"

# Train models
python -m src.models.train

# Run recommendations
python -c "from src.recommendation.engine import run_recommendation; run_recommendation('data/processed/features.parquet', 'data/processed/recommendations.csv')"

# Launch dashboard
streamlit run src/ui/app.py

# Launch API (development)
uvicorn src.api.main:app --reload --port 8000
```

## Docker Deployment

```bash
docker-compose up -d
# API at http://localhost:8000
# Dashboard at http://localhost:8501
# MLflow at http://localhost:5000
```

## Project Structure

```
src/
├── data/          # Ingestion, DuckDB, Parquet storage, validation
├── features/      # Feature engineering pipeline (52+ features)
├── models/        # XGBoost training, prediction, evaluation
├── recommendation/ # Recommendation engine, scoring, reason codes
├── explainability/ # SHAP explainer, surrogate trees
├── api/           # FastAPI REST endpoints
└── ui/            # Streamlit dashboard
```

## Key Features

- **69 engineered features** covering CTR, position, temporal trends, content freshness, competitive positioning, and interaction terms
- **Multi-label action classification** — protect, improve, refresh, rewrite, merge, prune, monitor
- **SHAP-based explainability** — every prediction comes with human-readable reason codes
- **Priority scoring** — combines model confidence, business impact, urgency, and action ease
- **Time-based train/validation/test split** — prevents data leakage in temporal search data
- **Dockerized** — one-command deployment with PostgreSQL, Redis, and MLflow

## Research Paper

See the [`paper/`](paper/) directory for the full research paper structure. The paper is publication-quality and covers methodology, feature engineering, model evaluation, limitations, and ethics.

## License

MIT
