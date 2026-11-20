
from pathlib import Path

import joblib
from fastapi import FastAPI

# Load the saved regression model
MODEL_PATH = Path(__file__).parent / "best_model.pkl"

model = joblib.load(MODEL_PATH)

# Initialize FastAPI
app = FastAPI(
    title="African Youth Unemployment API",
    description="Youth unemployment prediction using World Bank data",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "African Youth Unemployment API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }
