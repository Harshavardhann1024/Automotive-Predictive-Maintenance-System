"""
Prediction Agent — ML Inference Wrapper
========================================
Thin wrapper around the existing ML service.
Reuses the Singleton model loader, feature ordering, and domain-rule filtering.
Does NOT duplicate any business logic from services/ml_service.py.
"""

import logging
from typing import Dict, Any

from app.services.ml_service import predict_failure

logger = logging.getLogger("agents.prediction")


class PredictionAgent:
    """
    Wraps the existing ML service to provide a standardised prediction
    interface for the agent pipeline.

    Output format:
        {
            "probability": float,
            "risk_level": "LOW" | "MEDIUM" | "HIGH",
            "prediction": int,
            "sensor_flags": list[str],
            "threshold_used": float,
        }
    """

    @staticmethod
    def run(features: Dict[str, float]) -> Dict[str, Any]:
        """
        Execute ML inference on the given sensor features.

        Parameters
        ----------
        features : dict
            Must contain: engine_temp, oil_pressure, rpm,
            vibration, battery_voltage, mileage

        Returns
        -------
        dict — Normalised prediction result with risk_level
               in uppercase (LOW / MEDIUM / HIGH).
        """
        logger.info(
            "🔮 PredictionAgent: Running inference | "
            f"engine_temp={features.get('engine_temp')}, "
            f"oil_pressure={features.get('oil_pressure')}, "
            f"vibration={features.get('vibration')}"
        )

        # Delegate entirely to the existing ML service
        raw_result = predict_failure(features)

        # Normalise risk_level to uppercase for the agent pipeline
        normalised = {
            "probability": raw_result["failure_probability"],
            "risk_level": raw_result["risk_level"].upper(),  # LOW / MEDIUM / HIGH
            "prediction": raw_result["prediction"],
            "sensor_flags": raw_result["sensor_flags"],
            "threshold_used": raw_result["threshold_used"],
        }

        logger.info(
            f"🔮 PredictionAgent: Result → probability={normalised['probability']:.4f}, "
            f"risk_level={normalised['risk_level']}, prediction={normalised['prediction']}"
        )

        return normalised
