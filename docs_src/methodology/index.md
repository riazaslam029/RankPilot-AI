# Methodology

## ML Problem Formulation

The system predicts which pages need attention across 7 action dimensions simultaneously:
**Protect, Improve, Refresh, Rewrite, Merge, Prune, Monitor**

This is a **multi-output supervised learning** problem with two stages:
1. **Stage 1**: Multi-label classification — which actions apply to each page?
2. **Stage 2**: Scoring — how urgently should each action be taken?

## Feature Engineering

**69 features** across 6 domains:

| Category | Count | Examples |
|---|---|---|
| Engagement | 12 | CTR, position, impressions, clicks, CTR×Impressions |
| Temporal | 10 | CTR trend, position trend, growth rates, volatility |
| Content | 8 | Word count, title length, freshness, internal links |
| Competitive | 6 | Position bucket, cannibalization, SERP features |
| Behavioral | 8 | Dwell time proxy, pogo-stick proxy, click velocity |
| Interaction & Lag | 8 | CTR×log(impressions), lag features, rank velocity |

## Model Training

- **Algorithm**: XGBoost gradient boosted trees
- **Configuration**: binary:logistic per action, max_depth=6, learning_rate=0.05, n_estimators=500
- **Validation**: TimeSeriesSplit (5 folds, expanding window)
- **Label generation**: Weak supervision via SEO domain rules

## Explainability

- **SHAP**: Game-theoretic feature attribution for every prediction
- **Tiered explanations**: SHAP for data scientists, surrogate trees for executives, reason codes for practitioners
- **Trust mechanisms**: Confidence scores, feedback loops, historical trajectory
