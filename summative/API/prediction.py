
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).parent / "best_model.pkl"

FEATURES = [
    "gdp_growth",
    "gdp_per_capita",
    "inflation",
    "urban_population_pct",
    "population_growth",
    "agriculture_employment",
    "industry_employment",
    "female_labor_participation",
    "secondary_enrollment",
    "education_expenditure",
    "year",
    "income_group",
]

model = joblib.load(MODEL_PATH)

app = FastAPI(
    title="African Youth Unemployment API",
    description=(
        "Predict youth unemployment across African countries "
        "using World Bank indicators and machine learning."
    ),
    version="1.0.0",
)


class PredictionInput(BaseModel):
    gdp_growth: float
    gdp_per_capita: float = Field(ge=0)
    inflation: float
    urban_population_pct: float = Field(ge=0, le=100)
    population_growth: float
    agriculture_employment: float = Field(ge=0, le=100)
    industry_employment: float = Field(ge=0, le=100)
    female_labor_participation: float = Field(ge=0, le=100)
    secondary_enrollment: float | None = None
    education_expenditure: float | None = Field(default=None, ge=0)
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
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.post("/predict")
def predict(data: PredictionInput):
    try:
        payload = data.model_dump()
        dataframe = pd.DataFrame([payload], columns=FEATURES)

        prediction = float(model.predict(dataframe)[0])

        if not 0 <= prediction <= 100:
            raise ValueError("Prediction is outside the 0-100% range")

        return {
            "predicted_youth_unemployment_rate": round(prediction, 2),
            "unit": "percent",
            "model": "RandomForestRegressor",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed. Check the model and input compatibility.",
        ) from exc
