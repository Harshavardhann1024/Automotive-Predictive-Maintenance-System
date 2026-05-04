"""
ML Service — Singleton model loader + prediction engine
========================================================
Loads vehicle_failure_model_v4.pkl once at startup.
Provides predict_failure() with domain-rule FP filtering.
"""

import os
import logging
import numpy as np
import joblib
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# ─── Feature order must match training pipeline ───
FEATURE_ORDER = [
    "engine_temp",
    "oil_pressure",
    "rpm",
    "vibration",
    "battery_voltage",
    "mileage",
]

# ─── Risk classification thresholds ───
RISK_THRESHOLDS = {
    "low": 0.25,
    "medium": 0.50,
}


class _MLModelSingleton:
    """Thread-safe singleton that loads the model exactly once."""

    _instance: Optional["_MLModelSingleton"] = None
    _model = None
    _threshold: float = 0.30
    _use_domain_rules: bool = True
    _domain_rules: dict = {}
    _metadata: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load model from .pkl file (runs once)."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_dir, "vehicle_failure_model_v4.pkl")

        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(
                f"Trained model not found at {model_path}. "
                "Run train_model_v4.py first."
            )

        bundle = joblib.load(model_path)

        self._model = bundle["model"]
        self._threshold = bundle.get("threshold", 0.30)
        self._use_domain_rules = bundle.get("use_domain_rules", True)
        self._domain_rules = bundle.get("domain_rules", {})
        self._metadata = bundle.get("metrics", {})

        logger.info(
            f"✅ ML model loaded | threshold={self._threshold:.2f} | "
            f"domain_rules={'ON' if self._use_domain_rules else 'OFF'} | "
            f"accuracy={self._metadata.get('accuracy', 'N/A')}"
        )

    @property
    def model(self):
        return self._model

    @property
    def threshold(self):
        return self._threshold

    @property
    def use_domain_rules(self):
        return self._use_domain_rules

    @property
    def metadata(self):
        return self._metadata


def get_model() -> _MLModelSingleton:
    """Return the singleton model instance."""
    return _MLModelSingleton()


def classify_risk(probability: float) -> str:
    """
    Classify risk level based on failure probability.
    < 0.25 → Low  |  0.25–0.5 → Medium  |  > 0.5 → High
    """
    if probability > RISK_THRESHOLDS["medium"]:
        return "High"
    elif probability >= RISK_THRESHOLDS["low"]:
        return "Medium"
    return "Low"


def _apply_domain_rules(features: Dict[str, float]) -> bool:
    """
    Domain-rule filter: returns True if at least one sensor is in
    a concerning range (i.e. the prediction should be kept).
    """
    return (
        features.get("engine_temp", 0) > 100
        or features.get("oil_pressure", 999) < 35
        or features.get("vibration", 0) > 0.7
    )


def predict_failure(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Run the ML prediction pipeline.

    Parameters
    ----------
    features : dict
        Must contain keys: engine_temp, oil_pressure, rpm,
        vibration, battery_voltage, mileage

    Returns
    -------
    dict with:
        failure_probability  (float 0-1)
        prediction           (0 or 1)
        risk_level           ("Low" | "Medium" | "High")
        sensor_flags         (list of triggered domain rules)
        threshold_used       (float)
    """
    singleton = get_model()
    model = singleton.model

    # Build feature array in correct order
    feature_values = [float(features[f]) for f in FEATURE_ORDER]
    X = np.array([feature_values])

    # Get probability of failure (class 1)
    proba = model.predict_proba(X)[0, 1]
    failure_probability = round(float(proba), 4)

    # Threshold-based prediction
    raw_prediction = int(proba >= singleton.threshold)

    # Apply domain-rule FP filtering
    prediction = raw_prediction
    sensor_flags = []

    if raw_prediction == 1 and singleton.use_domain_rules:
        # Check which domain rules triggered
        if features.get("engine_temp", 0) > 100:
            sensor_flags.append("engine_temp > 100°C")
        if features.get("oil_pressure", 999) < 35:
            sensor_flags.append("oil_pressure < 35 psi")
        if features.get("vibration", 0) > 0.7:
            sensor_flags.append("vibration > 0.7 g")

        # If NO domain rule triggered, suppress the prediction (likely FP)
        if not _apply_domain_rules(features):
            prediction = 0

    # Risk classification uses raw probability regardless of domain filter
    risk_level = classify_risk(failure_probability)

    return {
        "failure_probability": failure_probability,
        "prediction": prediction,
        "risk_level": risk_level,
        "sensor_flags": sensor_flags,
        "threshold_used": singleton.threshold,
    }


def get_model_info() -> Dict[str, Any]:
    """Return metadata about the loaded model."""
    singleton = get_model()
    return {
        "model_version": "v4",
        "threshold": singleton.threshold,
        "domain_rules_active": singleton.use_domain_rules,
        "training_metrics": singleton.metadata,
        "feature_order": FEATURE_ORDER,
    }
