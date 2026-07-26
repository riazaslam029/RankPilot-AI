# RankPilot AI — Search Intelligence Platform

AI-powered Search Intelligence platform that analyzes search performance data and predicts which pages need action — with explainable recommendations.

## Quick Links

- [Architecture](architecture/index.html) — Complete system architecture
- [Methodology](methodology/index.html) — ML pipeline and feature engineering details
- [Results](results/index.html) — Model performance and feature importance
- [Downloads](downloads/index.html) — Paper, data, and model downloads
- [Paper (PDF)](paper/paper.pdf)
- [GitHub Repository](https://github.com/riazaslam029/RankPilot-AI)

## Summary

RankPilot AI classifies web pages into 7 actionable categories — **Protect, Improve, Refresh, Rewrite, Merge, Prune, Monitor** — using XGBoost multi-label classification with SHAP-based explainability.

**Key Metrics:**
- 71 engineered features across 6 domains
- Multi-label action classification with confidence scores
- 16 reason codes with human-readable explanations
- Priority scoring combining confidence, business impact, and urgency

