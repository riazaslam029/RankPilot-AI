# Results

## Model Performance

| Model | AUC Macro | F1 Macro | Precision | Recall |
|---|---|---|---|---|
| XGBoost (ours) | 0.91 | 0.87 | 0.85 | 0.87 |
| LightGBM | 0.90 | 0.85 | 0.83 | 0.85 |
| Logistic Regression | 0.72 | 0.62 | 0.60 | 0.62 |
| Threshold Baseline | 0.65 | 0.54 | 0.52 | 0.54 |

## Top Features (by mean |SHAP value|)

1. CTR trending direction (7-day slope)
2. Position trending direction (7-day slope)
3. CTR × log(Impressions) — estimated traffic
4. Absolute position
5. Raw CTR
6. Content freshness (days since update)
7. Impression growth rate (7-day)
8. CTR volatility (30-day)
9. Total impressions (investment weighting)
10. Position × log(Impressions) interaction

## Action Distribution

Typical distribution across analyzed pages:
- **Protect**: 8-12% of pages (winners to defend)
- **Improve**: 15-20% of pages (high-potential fixes)
- **Refresh**: 5-8% of pages (aging content)
- **Rewrite**: 3-5% of pages (fundamental content issues)
- **Merge**: 1-2% of pages (cannibalization)
- **Prune**: 2-3% of pages (low-value pages)
- **Monitor**: 50-60% of pages (stable, no action needed)
