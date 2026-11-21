
# African Youth Unemployment Prediction

## 1. Mission and Problem

My GCGO mission focuses on Job Creation and Education by addressing youth unemployment across Africa. 
Youth unemployment is influenced by economic, education, demographics, and labour-market structures. 
This project uses machine learning to estimate youth unemployment rates from World Bank indicators. 
The resulting model is accessible through a FastAPI backend and a Flutter mobile application.

## 2. Dataset and Source

The dataset was compiled using the World Bank's World Development Indicators (WDI), covering 54 African countries from 2000 to 2024.

It contains 1,350 country-year observations, with 1,193 observations retained for modelling. The target variable is the youth unemployment rate for ages 15–24.

Features include GDP growth, GDP per capita, inflation, population indicators, employment indicators, education expenditure, secondary school enrolment, year, and income group.

Source: https://databank.worldbank.org/source/world-development-indicators

The dataset collection script and CSV files are located in `summative/linear_regression/data/`.

## 3. Public Swagger API

The selected Random Forest model is deployed using FastAPI on Render.

Swagger documentation:
https://africa-youth-unemployment-api.onrender.com/docs

The API exposes:

- `GET /` — API information
- `GET /health` — Service and model status
- `POST /predict` — Youth unemployment prediction
- `POST /retrain` — Authenticated model retraining using a CSV upload

Retraining requires the `RETRAIN_API_KEY` environment variable and a matching `X-Retrain-Key` request header.

Retrained models are active on the current service instance. Permanent storage across Render restarts is not implemented.

## 4. YouTube Video Demo

https://youtu.be/DtOl2pthtk4

The demo covers the Flutter application, Swagger API testing, model training and evaluation, retraining, and CORS configuration.

## 5. Running the Flutter Mobile Application

### Prerequisites

- Flutter SDK installed
- Android Studio with an Android emulator, or a physical Android device
- VS Code or Android Studio
- An internet connection to access the deployed API

### Step 1: Clone the repository

```bash
git clone https://github.com/sultanhabibllah/linear_regression_model.git
cd linear_regression_model
```

### Step 2: Navigate to the Flutter project

```bash
cd summative/FlutterApp/youth_unemployment_app
```

### Step 3: Install Flutter dependencies

```bash
flutter pub get
```

### Step 4: Start an Android emulator

Launch an Android emulator using Android Studio or the VS Code device selector.

Check that Flutter detects the device:

```bash
flutter devices
```

### Step 5: Run the application

```bash
flutter run
```

### Step 6: Make a prediction

1. Enter the required economic, demographic, employment, and education indicators.
2. Select the appropriate income group.
3. Tap **Generate Prediction**.
4. The application sends the inputs to the deployed FastAPI backend.
5. The predicted youth unemployment rate appears on the screen.

The application validates inputs and displays an error when values do not meet the required constraints.

### API Development Setup

Python dependencies are managed using `uv`.

From the repository root:

```bash
cd summative/API
uv sync --frozen
uv run uvicorn prediction:app --reload
```

The local Swagger interface will be available at:

http://127.0.0.1:8000/docs

For local retraining, set the `RETRAIN_API_KEY` environment variable before starting the API.

The API loads `best_model.pkl` and uses the historical dataset stored under `summative/linear_regression/data/`.
