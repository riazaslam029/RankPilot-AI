# RankPilot AI — Repository Audit Report
## Version 1.0 | July 2026

---

## Executive Summary

The RankPilot AI project is a well-structured capstone submission with 75 files covering design documentation, ML pipeline, deployment, research, and GitHub Pages. However, the audit reveals **9 bugs**, **7 missing features**, **5 research quality issues**, **4 deployment issues**, and **6 code quality problems** that need addressing before submission.

---

## 1. STRENGTHS

| # | Strength | Details |
|---|---|---|
| S1 | Complete design document | 13-step design doc with 2,473 lines covering PM, architecture, ML, features, explainability, visualization, research, and self-critique |
| S2 | Modularity | Clean separation of concerns across `src/data/`, `src/features/`, `src/models/`, `src/recommendation/`, `src/explainability/`, `src/api/`, `src/ui/` |
| S3 | Feature engineering pipeline | 71 features across 6 domains with clear rationale docs |
| S4 | Production infrastructure | Docker, Docker Compose, CI/CD workflows, environment configs |
| S5 | Research paper | Full academic structure with abstract, related work, methodology, ethics |
| S6 | All imports resolve | 18 Python modules all import successfully with 0 errors |
| S7 | Working data pipeline | End-to-end: CSV ingestion → feature engineering → recommendations |
| S8 | GitHub Pages configuration | Deploy workflow, Quarto config, static HTML pages |
| S9 | Test structure | 4 test files with pytest fixtures covering all major modules |

---

## 2. WEAKNESSES

| # | Weakness | Impact |
|---|---|---|
| W1 | numpy-based model instead of XGBoost | Model quality is significantly lower than documented (numpy LR vs XGBoost) |
| W2 | Synthetic data only | Cannot prove real-world effectiveness |
| W3 | Weak supervision labels | Label noise not quantified or validated against expert annotations |
| W4 | Single-developer project | No review, no pair programming, no code standards enforcement |
| W5 | No A/B testing | Recommendations are unvalidated — cannot prove they improve outcomes |
| W6 | Missing real GSC data | The design doc promises Google Search Console integration; only synthetic data exists |
| W7 | Paper 813 words vs expected 3000+ | Significantly under-length for publication quality |
| W8 | No baseline comparison in paper | Claims of "0.87 F1" are fabricated/placeholder with no real training run |

---

## 3. BUGS (CRITICAL → LOW)

### B1 — API Schema Typo: `top_oppportunities` (3 p's)
**File:** `src/api/main.py` lines 26, 57, 64
**Bug:** `top_oppportunities` should be `top_opportunities`
**Impact:** Pydantic validation error — API responses will fail serialization
**Fix:** Rename all 3 occurrences

### B2 — Dead Code: `compute_lag_features()`
**File:** `src/features/pipeline.py` line 85
**Bug:** This function just sorts and returns the df — adds zero features
**Impact:** Misleading code, dead weight in pipeline, confusing for reviewers
**Fix:** Remove or implement lag features

### B3 — eval() Security Risk in reason_codes.py
**File:** `src/recommendation/reason_codes.py` line 117
**Bug:** Uses `eval()` with `__builtins__` restricted but still passes arbitrary dict
**Impact:** Potential code injection if feature values are user-controlled
**Fix:** Replace `eval()` with explicit condition checking or use `ast.literal_eval`

### B4 — Missing `__main__.py` for CLI commands
**File:** `src/models/` (missing `__main__.py`)
**Bug:** `python -m src.models.train` and `docker-entrypoint.sh train` will fail
**Impact:** Cannot run training from CLI
**Fix:** Create `src/models/__main__.py`

### B5 — Streamlit Deprecated API
**File:** `src/ui/app.py` lines 52, 65, 76
**Bug:** `st.plotly_chart(fig, use_container_width=True)` is deprecated
**Impact:** Warning messages in console; will break in Streamlit v2
**Fix:** Replace with `st.plotly_chart(fig, use_container_width="stretch")` or `st.plotly_chart(fig, width="stretch")`

### B6 — Docker Entrypoint: Missing `src.recommendation.cli`
**File:** `docker-entrypoint.sh` line 13
**Bug:** `python -m src.recommendation.cli` — no `cli.py` exists in `src/recommendation/`
**Impact:** `docker-entrypoint.sh analyze` will crash
**Fix:** Create `src/recommendation/cli.py` or remove the analyze command

### B7 — Missing `.dockerignore`
**File:** root (missing)
**Bug:** No `.dockerignore` file exists
**Impact:** Docker build copies unnecessary files (data, models, notebooks) into image
**Fix:** Create `.dockerignore` excluding `data/`, `models/`, `notebooks/`, `__pycache__/`, `.git/`

### B8 — Duplicate content in docs_src
**Files:** `docs_src/methodology/index.md` + `docs_src/methodology/index.html` (and same for results)
**Bug:** Both Markdown and HTML versions exist for same pages; Git Pages uses HTML
**Impact:** Markdown versions are dead code; confusion about which source is authoritative
**Fix:** Remove `.md` files, keep only `.html`; or convert everything to `.md` and let Quarto build both

### B9 — `deploy-pages.yml` references `_site` but copies from `docs_src/*`
**File:** `.github/workflows/deploy-pages.yml`
**Bug:** The workflow creates `_site/` and copies `docs_src/*` into it, but Quarto-style `_site` builds normally put everything there automatically. Since we removed Quarto, the `_site` directory is manually constructed but may not be cleaned between builds.
**Impact:** Stale files may persist in the deployed site
**Fix:** Add `rm -rf _site` before building; or use `actions/upload-pages-artifact` correctly

---

## 4. MISSING FEATURES (from design doc)

| # | Missing Feature | Design Doc Reference | Priority |
|---|---|---|---|
| M1 | XGBoost training (currently numpy LR) | Design doc Step 4 | CRITICAL |
| M2 | MLflow experiment tracking | Design doc Step 3 | High |
| M3 | LLM-powered natural language explanations | Design doc Step 2 V3 | Medium |
| M4 | A/B testing module | Design doc Step 2 V3 | Medium |
| M5 | Google Search Console API integration | Design doc Step 2 V2 | High |
| M6 | Automated retraining pipeline (cron) | Design doc Step 2 V2 | Medium |
| M7 | Alert system (Slack/email) | Design doc Step 2 V2 | Low |
| M8 | Ahrefs/SEMrush connector | Design doc Step 3 | Low |
| M9 | Multi-tenant authentication (V3) | Design doc Step 2 V3 | Low |
| M10 | SHAP waterfall chart in Streamlit dashboard | Design doc Step 7 | High |
| M11 | Per-page SHAP force plot | Design doc Step 7 | High |
| M12 | Model version comparison | Design doc Step 3 | Medium |
| M13 | CI/CD for model retraining | Design doc Step 3 | Medium |
| M14 | `requirements.txt` missing mlflow, duckdb, etc. | N/A | High |
| M15 | CONTRIBUTING.md | N/A | Medium |
| M16 | CHANGELOG.md | N/A | Medium |
| M17 | `.dockerignore` | N/A | Medium |

---

## 5. RESEARCH QUALITY ISSUES

| # | Issue | Severity |
|---|---|---|
| R1 | Paper uses fabricated metrics (0.87 F1, 0.91 XAI alignment) that don't correspond to actual model performance | HIGH |
| R2 | Paper is 813 words; publication-quality papers are typically 3000-6000 words | HIGH |
| R3 | No quantitative ablation study in the paper (design doc promised one) | MEDIUM |
| R4 | Only 5 citations in paper vs expected 10-15; all missing BibTeX entries | MEDIUM |
| R5 | No real GSC data means paper conclusions are based on synthetic data only | HIGH |
| R6 | Missing: data preprocessing details, feature correlation analysis, learning curves | MEDIUM |
| R7 | Missing: model comparison table with actual run numbers | HIGH |

---

## 6. DEPLOYMENT ISSUES

| # | Issue | Impact |
|---|---|---|
| D1 | GitHub Pages workflow uses `_site` manually built but `quarto render` removed | Medium — workflow may leave stale files |
| D2 | API endpoint `/analyze` processes 360K rows without chunking/streaming | Medium — will timeout for large datasets |
| D3 | FastAPI CORS allows `["*"]` — should restrict to Streamlit origin in production | Low |
| D4 | No `.dockerignore` — bloats Docker image | Low |

---

## 7. CODE QUALITY ISSUES

| # | Issue | File |
|---|---|---|
| C1 | `use_container_width` deprecated parameter | `src/ui/app.py` |
| C2 | `eval()` in reason_codes.py | `src/recommendation/reason_codes.py` |
| C3 | Dead function `compute_lag_features()` in pipeline | `src/features/pipeline.py` |
| C4 | `train.py` imports xgboost but has numpy fallback without trying import | `src/models/train.py` |
| C5 | `evaluate.py` imports sklearn but it may not be installed at runtime | `src/models/evaluate.py` |
| C6 | `shap_explainer.py` imports shap which may not be installed | `src/explainability/shap_explainer.py` |

---

## 8. IMPROVEMENTS RANKED BY IMPACT

| Rank | Improvement | Impact | Effort | Category |
|---|---|---|---|---|
| 1 | **Fix API typo `top_oppportunities` → `top_opportunities`** | CRITICAL — API broken | 2 min | Bug |
| 2 | **Replace eval() with safe condition checking** | HIGH — security risk | 15 min | Bug |
| 3 | **Remove dead `compute_lag_features()` or implement it** | HIGH — code clarity | 10 min | Bug |
| 4 | **Create `src/recommendation/cli.py` for docker-entrypoint analyze** | HIGH — deploy broken | 20 min | Bug |
| 5 | **Create `src/models/__main__.py` for CLI training** | HIGH — deploy broken | 10 min | Bug |
| 6 | **Fix Streamlit deprecated `use_container_width`** | MEDIUM — console spam | 5 min | Bug |
| 7 | **Create `.dockerignore`** | MEDIUM — Docker image size | 5 min | Deployment |
| 8 | **Fix `deploy-pages.yml` to clean `_site` before build** | MEDIUM — stale files | 5 min | Deployment |
| 9 | **Remove duplicate `.md` files from docs_src/** | MEDIUM — confusion | 2 min | Bug |
| 10 | **Create `CONTRIBUTING.md`** | LOW — project professionalism | 15 min | Quality |
| 11 | **Create `CHANGELOG.md`** | LOW — project professionalism | 10 min | Quality |
| 12 | **Update paper with real metrics and longer body** | HIGH — research quality | 2 hrs | Research |
| 13 | **Add real GSC data to supplement synthetic data** | HIGH — credibility | 30 min | Data |
| 14 | **Add SHAP waterfall/force plot to Streamlit dashboard** | MEDIUM — explainability demo | 1 hr | Feature |
| 15 | **Fix requirements.txt to include all dependencies** | MEDIUM — install reliability | 10 min | Deployment |

---

## 9. SUMMARY SCORECARD

| Area | Score | Max | Notes |
|---|---|---|---|
| Design Document | 9/10 | 10 | Excellent — comprehensive 13-step design |
| Code Architecture | 8/10 | 10 | Clean modular structure; some dead code |
| Feature Engineering | 8/10 | 10 | 71 features well-documented; SQL generator incomplete |
| ML Pipeline | 4/10 | 10 | numpy LR instead of XGBoost; placeholder metrics |
| Recommendation Engine | 6/10 | 10 | Rule-based scoring works; reason_codes eval() bug |
| Explainability | 4/10 | 10 | SHAP module coded but not integrated with live pipeline |
| Dashboard | 7/10 | 10 | Functional Streamlit app; deprecated API calls |
| API | 4/10 | 10 | Typo in schema breaks serialization |
| Research Paper | 3/10 | 10 | Placeholder metrics, under-length, missing details |
| GitHub Pages | 7/10 | 10 | Ready for deployment; duplicate content |
| CI/CD | 7/10 | 10 | Workflows present; Pages workflow needs fix |
| Tests | 5/10 | 10 | Structure exists; no actual test execution |
| Docker | 6/10 | 10 | Good multi-service compose; missing .dockerignore |
| Documentation | 6/10 | 10 | README good; missing CONTRIBUTING.md, CHANGELOG.md |
| **Overall** | **6.1/10** | **10** | Strong foundation; needs bug fixes and paper quality |

---

*End of Audit Report*
