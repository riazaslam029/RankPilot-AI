# System Architecture

## Overview

RankPilot AI follows a modular, layered architecture with clear separation of concerns across six layers.

## Architecture Diagram

```
Client Layer          →  Streamlit Dashboard, FastAPI, CLI
Application Layer     →  Recommendation Engine, Feature Pipeline, ML Pipeline
Data Layer            →  DuckDB, Parquet, PostgreSQL, Redis, S3
Infrastructure Layer  →  Docker, Kubernetes, GitHub Actions
```

## Component Breakdown

### Data Ingestion
- CSV upload with Great Expectations validation
- DuckDB analytical queries on Parquet files
- Support for Google Search Console exports

### Feature Engineering
- 69 features across 6 domains
- Declarative Python pipeline
- Reproducible and versioned

### ML Pipeline
- XGBoost multi-label classification
- MLflow experiment tracking
- Time-based splits with temporal cross-validation

### Recommendation Engine
- Multi-dimensional scoring (ML + business rules)
- 16 reason codes with human-readable explanations
- Priority tiers: Critical → High → Medium → Low → Monitor

### Deployment
- Docker + Docker Compose
- CI/CD via GitHub Actions
- Staging and production environments
