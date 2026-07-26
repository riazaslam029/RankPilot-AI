from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="RankPilot AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    data_path: str
    output_path: Optional[str] = None


class AnalyzeResponse(BaseModel):
    status: str
    pages_analyzed: int
    primary_actions: dict[str, int]
    top_oppportunities: list[dict]


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rankpilot-ai"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    from src.data.ingestion import ingest_csv, prepare_for_feature_engineering
    from src.features.pipeline import run_feature_pipeline
    from src.recommendation.engine import run_recommendation

    try:
        df = ingest_csv(request.data_path)
        df = prepare_for_feature_engineering(df)
        feature_path = str(request.data_path).replace(".csv", "_features.parquet")
        run_feature_pipeline(str(request.data_path), feature_path)
        result_path = run_recommendation(feature_path, str(request.data_path).replace(".csv", "_recommendations.csv"))
        import pandas as pd
        results = pd.read_csv(result_path)
        actions = results["primary_action"].value_counts().to_dict()
        top = results.head(10).to_dict("records")
        for entry in top:
            entry["all_scores"] = str(entry.get("all_scores", ""))
            entry["reason_codes"] = str(entry.get("reason_codes", ""))
        return AnalyzeResponse(
            status="complete",
            pages_analyzed=len(results),
            primary_actions=actions,
            top_oppportunities=top,
        )
    except Exception as e:
        return AnalyzeResponse(
            status="error",
            pages_analyzed=0,
            primary_actions={},
            top_oppportunities=[],
        )
