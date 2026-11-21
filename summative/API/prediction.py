
from pathlib import Path
from threading import Lock

import joblib
import numpy as np
import pandas as pd
from fastapi import (
    FastAPI,
    File,
    Header,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from retrain import FEATURES, retrain_model


API_DIR = Path(__file__).resolve().parent
MODEL_PATH = API_DIR / "best_model.pkl"

# Shared state is updated when retraining succeeds.
model_lock = Lock()

model_state = {
    "model": joblib.load(MODEL_PATH),
    "version": "original",
}

app = FastAPI(
    title="African Youth Unemployment API",
    description=(
        "Predict and retrain youth unemployment models "
        "using World Bank economic and education indicators."
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class PredictionInput(BaseModel):
    gdp_growth: float
    gdp_per_capita: float = Field(ge=0)
    inflation: float
    urban_population_pct: float = Field(ge=0, le=100)
    population_growth: float
    agriculture_employment: float = Field(ge=0, le=100)
    industry_employment: float = Field(ge=0, le=100)
    female_labor_participation: float = Field(
        ge=0, le=100
    )
    secondary_enrollment: float | None = None
    education_expenditure: float | None = Field(
        default=None, ge=0
    )
    year: int = Field(ge=2000, le=2100)
    income_group: str = Field(min_length=1)


@app.get("/")
def home():
    return {
        "message": "African Youth Unemployment API",
        "status": "running",
    }


@app.get("/health")
def health():
    with model_lock:
        version = model_state["version"]
        loaded = model_state["model"] is not None

    return {
        "status": "healthy",
        "model_loaded": loaded,
        "model_version": version,
    }


@app.post("/predict")
def predict(data: PredictionInput):
    try:
        dataframe = pd.DataFrame(
            [data.model_dump()],
            columns=FEATURES,
        )

        with model_lock:
            prediction = float(
                model_state["model"].predict(dataframe)[0]
            )
            version = model_state["version"]

        if not np.isfinite(prediction):
            raise ValueError("Prediction is not finite.")

        if not 0 <= prediction <= 100:
            raise ValueError(
                "Prediction is outside the 0-100% range."
            )

        return {
            "predicted_youth_unemployment_rate": round(
                prediction, 2
            ),
            "unit": "percent",
            "model": "RandomForestRegressor",
            "model_version": version,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed.",
        ) from exc


@app.post("/retrain")
def retrain(
    file: UploadFile = File(...),
    x_retrain_key: str | None = Header(default=None),
):
    return retrain_model(
        file=file,
        x_retrain_key=x_retrain_key,
        model_state=model_state,
        model_lock=model_lock,
    )
