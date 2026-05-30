"""FastAPI service for Flight Delay Prediction inference."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from src.flight_delay_features import (
        DEFAULT_THRESHOLD,
        MODEL_ARTIFACT_PATH,
        MODEL_FEATURES,
        validate_feature_payload,
    )
except ModuleNotFoundError:
    from flight_delay_features import (  # type: ignore[no-redef]
        DEFAULT_THRESHOLD,
        MODEL_ARTIFACT_PATH,
        MODEL_FEATURES,
        validate_feature_payload,
    )


class PredictionRequest(BaseModel):
    """Generic feature payload for one flight."""

    features: dict[str, float] = Field(
        ...,
        description="Dictionary with all model features required for inference.",
        examples=[
            {
                "HOUR_OF_DAY": 17,
                "IS_PEAK_HOUR": 1,
                "IS_WEEKEND": 0,
                "IS_HIGH_SEASON": 1,
                "CASCADING_DELAY_FLAG": 1,
                "ROUTE_DELAY_RATE": 0.24,
                "AIRLINE_DELAY_RATE": 0.21,
                "AIRLINE_ENC": 3,
                "DISTANCE": 740,
                "DEPARTURE_DELAY": 18,
                "MONTH": 7,
                "DAY_OF_WEEK": 5,
                "AIR_SYSTEM_DELAY": 10,
                "WEATHER_DELAY": 0,
            }
        ],
    )


class PredictionResponse(BaseModel):
    model_name: str
    threshold: float
    delay_probability: float
    is_delayed_prediction: bool
    risk_level: str
    features_used: list[str]


app = FastAPI(
    title="Flight Delay Prediction API",
    description="API para predecir si un vuelo tendra retraso mayor a 15 minutos.",
    version="1.0.0",
)

_model_bundle: dict[str, Any] | None = None


def load_model_bundle() -> dict[str, Any]:
    """Load model artifact once and cache it for subsequent requests."""
    global _model_bundle

    if _model_bundle is not None:
        return _model_bundle

    artifact_path = Path(MODEL_ARTIFACT_PATH)
    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {artifact_path}. "
            "Run the packaging cell in the training notebook first."
        )

    loaded_bundle = joblib.load(artifact_path)
    if not isinstance(loaded_bundle, dict) or "model" not in loaded_bundle:
        raise ValueError("Invalid model artifact. Expected a dictionary with a 'model' key.")

    _model_bundle = loaded_bundle
    return loaded_bundle


def classify_risk(probability: float) -> str:
    if probability >= 0.85:
        return "high"
    if probability >= 0.60:
        return "medium"
    return "low"


@app.get("/health")
def health() -> dict[str, Any]:
    """Health check used by notebooks and external consumers."""
    try:
        bundle = load_model_bundle()
        model_loaded = True
        model_name = bundle.get("model_name", "unknown")
    except Exception as exc:
        model_loaded = False
        model_name = "unavailable"
        return {
            "status": "degraded",
            "model_loaded": model_loaded,
            "model_name": model_name,
            "detail": str(exc),
        }

    return {
        "status": "ok",
        "model_loaded": model_loaded,
        "model_name": model_name,
        "features": MODEL_FEATURES,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest) -> PredictionResponse:
    """Predict delay probability for one flight."""
    try:
        bundle = load_model_bundle()
        features = bundle.get("features", MODEL_FEATURES)
        ordered_payload = validate_feature_payload(request.features)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    model = bundle["model"]
    threshold = float(bundle.get("threshold", DEFAULT_THRESHOLD))
    model_name = str(bundle.get("model_name", model.__class__.__name__))

    input_df = pd.DataFrame([[ordered_payload[feature] for feature in features]], columns=features)

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(input_df)[0][1])
    else:
        probability = float(model.predict(input_df)[0])

    return PredictionResponse(
        model_name=model_name,
        threshold=threshold,
        delay_probability=round(probability, 6),
        is_delayed_prediction=probability >= threshold,
        risk_level=classify_risk(probability),
        features_used=list(features),
    )
