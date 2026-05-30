"""Shared feature contract for the flight delay model."""

from __future__ import annotations

from typing import Any

MODEL_FEATURES: list[str] = [
    "HOUR_OF_DAY",
    "IS_PEAK_HOUR",
    "IS_WEEKEND",
    "IS_HIGH_SEASON",
    "CASCADING_DELAY_FLAG",
    "ROUTE_DELAY_RATE",
    "AIRLINE_DELAY_RATE",
    "AIRLINE_ENC",
    "DISTANCE",
    "DEPARTURE_DELAY",
    "MONTH",
    "DAY_OF_WEEK",
    "AIR_SYSTEM_DELAY",
    "WEATHER_DELAY",
]

TARGET = "IS_DELAYED"
DEFAULT_THRESHOLD = 0.85
MODEL_ARTIFACT_PATH = "models/flight_delay_model.joblib"

FEATURE_DESCRIPTIONS: dict[str, str] = {
    "HOUR_OF_DAY": "Scheduled departure hour derived from SCHEDULED_DEPARTURE.",
    "IS_PEAK_HOUR": "Flag for flights scheduled between 3 PM and 8 PM.",
    "IS_WEEKEND": "Flag for Saturday/Sunday flights.",
    "IS_HIGH_SEASON": "Flag for high-travel months: Jan, Jun, Jul, Aug, Dec.",
    "CASCADING_DELAY_FLAG": "Flag indicating prior aircraft-related delay signal.",
    "ROUTE_DELAY_RATE": "Historical delay rate for origin-destination route.",
    "AIRLINE_DELAY_RATE": "Historical delay rate for the airline.",
    "AIRLINE_ENC": "Numeric encoding of airline code from training.",
    "DISTANCE": "Flight distance in miles.",
    "DEPARTURE_DELAY": "Departure delay in minutes when available.",
    "MONTH": "Scheduled flight month.",
    "DAY_OF_WEEK": "Scheduled day of week from dataset.",
    "AIR_SYSTEM_DELAY": "Air system delay minutes when available.",
    "WEATHER_DELAY": "Weather delay minutes when available.",
}


def validate_feature_payload(payload: dict[str, Any]) -> dict[str, float]:
    """Validate and order incoming feature values for model inference."""
    missing_features = [feature for feature in MODEL_FEATURES if feature not in payload]
    if missing_features:
        joined = ", ".join(missing_features)
        raise ValueError(f"Missing required features: {joined}")

    ordered_payload: dict[str, float] = {}
    invalid_features: list[str] = []

    for feature in MODEL_FEATURES:
        value = payload[feature]
        try:
            ordered_payload[feature] = float(value)
        except (TypeError, ValueError):
            invalid_features.append(feature)

    if invalid_features:
        joined = ", ".join(invalid_features)
        raise ValueError(f"Features must be numeric: {joined}")

    return ordered_payload


def build_model_bundle(
    model: Any,
    *,
    model_name: str = "XGBoost",
    threshold: float = DEFAULT_THRESHOLD,
    features: list[str] | None = None,
) -> dict[str, Any]:
    """Create the serializable model package consumed by the API."""
    return {
        "model": model,
        "model_name": model_name,
        "threshold": threshold,
        "features": features or MODEL_FEATURES,
        "target": TARGET,
        "feature_descriptions": FEATURE_DESCRIPTIONS,
    }
