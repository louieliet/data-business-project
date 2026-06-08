from __future__ import annotations

from typing import Any

# Estas son las columnas exactas que el modelo espera recibir en inferencia.
# El orden importa porque despues construimos un DataFrame con estas features
# antes de llamar a model.predict().
MODEL_FEATURES: list[str] = [
    "HOUR_OF_DAY",
    "IS_PEAK_HOUR",
    "IS_WEEKEND",
    "IS_HIGH_SEASON",
    "CASCADING_DELAY_FLAG",
    "ROUTE_AVG_DELAY",
    "AIRLINE_AVG_DELAY",
    "AIRLINE_ENC",
    "DISTANCE",
    "DEPARTURE_DELAY",
    "MONTH",
    "DAY_OF_WEEK",
    "AIR_SYSTEM_DELAY",
    "WEATHER_DELAY",
]

# La etiqueta del modelo es numerica: minutos de retraso de llegada.
# Esto confirma que el proyecto usa regresion, no clasificacion.
TARGET = "ARRIVAL_DELAY"

# Ruta relativa donde FastAPI busca el modelo empaquetado generado por el notebook.
MODEL_ARTIFACT_PATH = "models/flight_delay_model.joblib"

# Diccionario de apoyo para documentar que significa cada variable.
# No es estrictamente necesario para predecir, pero ayuda a explicar el contrato del modelo.
FEATURE_DESCRIPTIONS: dict[str, str] = {
    "HOUR_OF_DAY": "Scheduled departure hour derived from SCHEDULED_DEPARTURE.",
    "IS_PEAK_HOUR": "Flag for flights scheduled between 3 PM and 8 PM.",
    "IS_WEEKEND": "Flag for Saturday/Sunday flights.",
    "IS_HIGH_SEASON": "Flag for high-travel months: Jan, Jun, Jul, Aug, Dec.",
    "CASCADING_DELAY_FLAG": "Flag indicating prior aircraft-related delay signal.",
    "ROUTE_AVG_DELAY": "Historical average arrival delay for origin-destination route.",
    "AIRLINE_AVG_DELAY": "Historical average arrival delay for the airline.",
    "AIRLINE_ENC": "Numeric encoding of airline code from training.",
    "DISTANCE": "Flight distance in miles.",
    "DEPARTURE_DELAY": "Departure delay in minutes when available.",
    "MONTH": "Scheduled flight month.",
    "DAY_OF_WEEK": "Scheduled day of week from dataset.",
    "AIR_SYSTEM_DELAY": "Air system delay minutes when available.",
    "WEATHER_DELAY": "Weather delay minutes when available.",
}


def validate_feature_payload(payload: dict[str, Any]) -> dict[str, float]:
    # Primero verificamos que el request traiga todas las variables requeridas.
    # Si falta alguna, la API devuelve un error claro en vez de fallar silenciosamente.
    missing_features = [feature for feature in MODEL_FEATURES if feature not in payload]
    if missing_features:
        joined = ", ".join(missing_features)
        raise ValueError(f"Missing required features: {joined}")

    ordered_payload: dict[str, float] = {}
    invalid_features: list[str] = []

    # Convertimos todos los valores a float porque los modelos de scikit-learn
    # esperan datos numericos. Tambien preservamos el orden de MODEL_FEATURES.
    for feature in MODEL_FEATURES:
        value = payload[feature]
        try:
            ordered_payload[feature] = float(value)
        except (TypeError, ValueError):
            invalid_features.append(feature)

    # Si alguna variable no puede convertirse a numero, reportamos cuales son.
    if invalid_features:
        joined = ", ".join(invalid_features)
        raise ValueError(f"Features must be numeric: {joined}")

    return ordered_payload


def build_model_bundle(
    model: Any,
    *,
    model_name: str = "XGBoost Regressor",
    features: list[str] | None = None,
) -> dict[str, Any]:
    # Este bundle es lo que se guarda con joblib.
    # Incluye el modelo entrenado y metadata para que la API sepa como usarlo.
    return {
        "model": model,
        "model_name": model_name,
        "features": features or MODEL_FEATURES,
        "target": TARGET,
        "feature_descriptions": FEATURE_DESCRIPTIONS,
    }
