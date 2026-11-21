
import io
import os
import secrets
import tempfile
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile
from sklearn.base import clone


API_DIR = Path(__file__).resolve().parent
MODEL_PATH = API_DIR / "best_model.pkl"
DATA_PATH = (
    API_DIR.parent
    / "linear_regression"
    / "data"
    / "africa_youth_unemployment.csv"
)

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

TARGET = "youth_unemployment_rate"

BASE_FEATURES = [
    "gdp_growth",
    "gdp_per_capita",
    "inflation",
    "urban_population_pct",
    "population_growth",
    "agriculture_employment",
    "industry_employment",
    "female_labor_participation",
]

NUMERIC_FEATURES = [
    name for name in FEATURES if name != "income_group"
]

PERCENT_FEATURES = [
    "urban_population_pct",
    "agriculture_employment",
    "industry_employment",
    "female_labor_participation",
]

MAX_UPLOAD_BYTES = 2 * 1024 * 1024


def validate_training_data(frame: pd.DataFrame):
    required = FEATURES + [TARGET]

    missing = [
        column for column in required
        if column not in frame.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    if frame.empty:
        raise ValueError("The uploaded CSV is empty.")

    frame = frame[required].copy()

    for column in NUMERIC_FEATURES + [TARGET]:
        frame[column] = pd.to_numeric(
            frame[column],
            errors="raise",
        )

    for column in NUMERIC_FEATURES + [TARGET]:
        values = frame[column].dropna().to_numpy(
            dtype=float
        )

        if not np.isfinite(values).all():
            raise ValueError(
                f"{column} contains infinite values."
            )

    required_numeric = [
        column for column in NUMERIC_FEATURES
        if column not in (
            "secondary_enrollment",
            "education_expenditure",
        )
    ]

    if frame[required_numeric + [TARGET]].isna().any().any():
        raise ValueError(
            "Required numeric inputs and target cannot be empty."
        )

    for column in PERCENT_FEATURES + [TARGET]:
        if not frame[column].between(0, 100).all():
            raise ValueError(
                f"{column} must be between 0 and 100."
            )

    if (frame["gdp_per_capita"] < 0).any():
        raise ValueError(
            "GDP per capita cannot be negative."
        )

    if (frame["education_expenditure"].dropna() < 0).any():
        raise ValueError(
            "Education expenditure cannot be negative."
        )

    if not frame["year"].between(2000, 2100).all():
        raise ValueError(
            "Year must be between 2000 and 2100."
        )

    if not (frame["year"] % 1 == 0).all():
        raise ValueError(
            "Year must contain whole numbers."
        )

    valid_groups = {
        "Low income",
        "Lower middle income",
        "Upper middle income",
        "High income",
    }

    if (
        frame["income_group"].isna().any()
        or not frame["income_group"].isin(valid_groups).all()
    ):
        raise ValueError(
            "Invalid or missing income_group category."
        )

    return frame


def retrain_model(
    file: UploadFile,
    x_retrain_key: str | None,
    model_state: dict,
    model_lock,
):
    expected_key = os.getenv("RETRAIN_API_KEY")

    if (
        not expected_key
        or not x_retrain_key
        or not secrets.compare_digest(
            x_retrain_key,
            expected_key,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized retraining request.",
        )

    if (
        not file.filename
        or not file.filename.lower().endswith(".csv")
    ):
        raise HTTPException(
            status_code=400,
            detail="Upload a CSV file.",
        )

    contents = file.file.read(MAX_UPLOAD_BYTES + 1)

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="CSV exceeds the 2 MB upload limit.",
        )

    try:
        uploaded = pd.read_csv(io.BytesIO(contents))
        uploaded = validate_training_data(uploaded)

        historical = pd.read_csv(DATA_PATH)

        # Keep historical observations with the
        # essential baseline predictors and target.
        historical = historical.dropna(
            subset=BASE_FEATURES + [
                "year",
                "income_group",
                TARGET,
            ]
        )

        historical = validate_training_data(historical)

        # Combine historical and uploaded observations.
        combined = pd.concat(
            [historical, uploaded],
            ignore_index=True,
        )

        features = combined[FEATURES]
        target = combined[TARGET]

        # Refit a fresh copy of the original pipeline.
        original_pipeline = joblib.load(MODEL_PATH)
        new_model = clone(original_pipeline)

        new_model.fit(features, target)

        # Confirm the new model produces a finite value.
        sample_prediction = float(
            new_model.predict(features.iloc[[0]])[0]
        )

        if not np.isfinite(sample_prediction):
            raise ValueError(
                "Retrained model produced an invalid result."
            )

        # Save separately from the original model.
        runtime_path = API_DIR / "retrained_model.pkl"
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                dir=API_DIR,
                prefix="retrained_",
                suffix=".pkl",
                delete=False,
            ) as temp:
                temp_path = Path(temp.name)

            joblib.dump(new_model, temp_path)

            # Save and activate the updated model
            # while holding the shared lock.
            with model_lock:
                os.replace(temp_path, runtime_path)
                temp_path = None

                model_state["model"] = new_model
                model_state["version"] = "retrained"

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

        return {
            "message": "Model retrained successfully",
            "model": "RandomForestRegressor",
            "original_rows": len(historical),
            "new_rows": len(uploaded),
            "total_training_rows": len(combined),
            "model_version": model_state["version"],
            "persistence": "current service instance only",
        }

    except (
        ValueError,
        KeyError,
        pd.errors.ParserError,
        UnicodeDecodeError,
    ) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Model retraining failed.",
        ) from exc
