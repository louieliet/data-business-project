from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Este bloque permite que el archivo funcione tanto cuando se importa como paquete
# desde la raiz del proyecto (`src.flight_delay_features`) como cuando se ejecuta
# desde dentro de la carpeta `src`.
try:
    from src.flight_delay_features import (
        MODEL_ARTIFACT_PATH,
        MODEL_FEATURES,
        validate_feature_payload,
    )
except ModuleNotFoundError:
    from flight_delay_features import (
        MODEL_ARTIFACT_PATH,
        MODEL_FEATURES,
        validate_feature_payload,
    )


class PredictionRequest(BaseModel):
    # Este modelo define la estructura esperada del request.
    # La API recibe un diccionario llamado features con las variables del vuelo.
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
                "ROUTE_AVG_DELAY": 12.4,
                "AIRLINE_AVG_DELAY": 9.8,
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
    # Esta es la respuesta que regresa /predict.
    # La salida principal es predicted_arrival_delay_minutes, no una clase.
    model_name: str
    predicted_arrival_delay_minutes: float
    risk_level: str
    features_used: list[str]


# Creamos la instancia principal de FastAPI.
# Esta app es la que uvicorn levanta en Colab y luego ngrok expone publicamente.
app = FastAPI(
    title="Flight Delay Prediction API",
    description="API para estimar minutos de retraso de llegada de un vuelo.",
    version="1.0.0",
)

# Cache global del modelo.
# Sirve para cargar el .joblib una sola vez y reutilizarlo en predicciones posteriores.
_model_bundle: dict[str, Any] | None = None


def load_model_bundle() -> dict[str, Any]:
    global _model_bundle

    # Si el modelo ya fue cargado, lo regresamos desde memoria.
    # Esto evita leer Google Drive en cada request.
    if _model_bundle is not None:
        return _model_bundle

    artifact_path = Path(MODEL_ARTIFACT_PATH)
    if not artifact_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {artifact_path}. "
            "Run the packaging cell in the training notebook first."
        )

    # joblib carga el bundle generado por el notebook de entrenamiento.
    # Ese bundle contiene el modelo y metadata como features y target.
    loaded_bundle = joblib.load(artifact_path)
    if not isinstance(loaded_bundle, dict) or "model" not in loaded_bundle:
        raise ValueError("Invalid model artifact. Expected a dictionary with a 'model' key.")

    _model_bundle = loaded_bundle
    return loaded_bundle


def classify_risk(predicted_minutes: float) -> str:
    # Esta funcion traduce minutos estimados a una categoria operativa.
    # El modelo sigue siendo regresion; esta capa solo ayuda a negocio.
    if predicted_minutes >= 45:
        return "high"
    if predicted_minutes > 15:
        return "medium"
    return "low"


@app.get("/health")
def health() -> dict[str, Any]:
    # Endpoint para revisar si la API puede cargar el modelo.
    # Si algo falla, responde degraded con el detalle del error.
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
    # Cargamos el modelo y validamos que el payload tenga todas las features.
    try:
        bundle = load_model_bundle()
        features = bundle.get("features", MODEL_FEATURES)
        ordered_payload = validate_feature_payload(request.features)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    model = bundle["model"]
    model_name = str(bundle.get("model_name", model.__class__.__name__))

    # Convertimos el payload a DataFrame para mantener la misma estructura
    # que el modelo uso durante entrenamiento.
    input_df = pd.DataFrame([[ordered_payload[feature] for feature in features]], columns=features)

    # Como el modelo es regresor, usamos predict() para obtener minutos estimados.
    predicted_minutes = float(model.predict(input_df)[0])

    return PredictionResponse(
        model_name=model_name,
        predicted_arrival_delay_minutes=round(predicted_minutes, 2),
        risk_level=classify_risk(predicted_minutes),
        features_used=list(features),
    )
