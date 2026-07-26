#!/bin/bash
set -e

if [ "$1" = "api" ]; then
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
elif [ "$1" = "ui" ]; then
    streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0
elif [ "$1" = "train" ]; then
    python -m src.models.train
elif [ "$1" = "analyze" ]; then
    python -m src.recommendation.cli
else
    exec "$@"
fi
