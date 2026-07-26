import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.recommendation.engine import run_recommendation
from src.utils.config import settings

if __name__ == "__main__":
    feature_path = str(settings.processed_dir / "features.parquet")
    output_path = str(settings.processed_dir / "recommendations.csv")
    run_recommendation(feature_path, output_path)
