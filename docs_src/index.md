# RankPilot AI — Search Intelligence Platform

AI-powered Search Intelligence platform that analyzes search performance data and predicts which pages need action — with explainable recommendations.

## Quick Links

- [Architecture Diagram](architecture/index.md) — Complete system architecture
- [Methodology](methodology/index.md) — ML pipeline and feature engineering details
- [Results](results/index.md) — Model performance and feature importance
- [Paper (PDF)](../paper/paper.pdf) — Download full research paper
- [GitHub Repository](https://github.com/username/rankpilot-ai) — Source code
- [Streamlit Dashboard](https://rankpilot-streamlit-app.streamlit.app) — Live demo

## Summary

RankPilot AI classifies web pages into 7 actionable categories — **Protect, Improve, Refresh, Rewrite, Merge, Prune, Monitor** — using XGBoost multi-label classification with SHAP-based explainability.

**Key Metrics:**
- 69 engineered features across 6 domains
- XGBoost model achieving 0.87 macro F1-score
- 91% SHAP explanation alignment with domain experts
- Multi-dimensional priority scoring combining confidence, business impact, and urgency
