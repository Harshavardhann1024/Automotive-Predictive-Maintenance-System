"""
ML Service — Singleton model loader + prediction engine + SHAP Explainability
================================================================================
Loads ml/models/vehicle_failure_model_v4.pkl once at startup.
Provides predict_failure() with domain-rule FP filtering.
Optionally computes SHAP explanations for interpretable predictions.
"""

import os
import time
import logging
import numpy as np
import joblib
import shap
from typing import Dict, Any, Optional, List

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

# ─── Human-readable feature labels for explanations ───
FEATURE_LABELS = {
    "engine_temp": "Engine Temperature",
    "oil_pressure": "Oil Pressure",
    "rpm": "Engine RPM",
    "vibration": "Vibration Level",
    "battery_voltage": "Battery Voltage",
    "mileage": "Mileage",
}

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
    _shap_explainer: Optional[shap.TreeExplainer] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        """Load model from .pkl file (runs once)."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = os.path.join(base_dir, "ml/models/vehicle_failure_model_v4.pkl")

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

    def _init_shap_explainer(self):
        """
        Lazily initialize the SHAP TreeExplainer.
        Called only on the first explain request to avoid startup latency.
        Cached for all subsequent calls (Singleton pattern).
        """
        if self._shap_explainer is None:
            start = time.time()
            self._shap_explainer = shap.TreeExplainer(self._model)
            elapsed = time.time() - start
            logger.info(f"✅ SHAP TreeExplainer initialized in {elapsed:.2f}s")
        return self._shap_explainer

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

    @property
    def shap_explainer(self):
        """Returns the cached SHAP explainer, initializing if needed."""
        return self._init_shap_explainer()


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


def _compute_shap_explanations(
    X: np.ndarray,
    singleton: _MLModelSingleton,
) -> List[Dict[str, Any]]:
    """
    Compute SHAP values for a single prediction instance.

    Returns a list of feature explanations sorted by absolute impact
    (descending), e.g.:
      [{"feature": "engine_temp", "impact": +0.32, "value": 118.0}, ...]
    """
    explainer = singleton.shap_explainer
    shap_values = explainer.shap_values(X)

    # shap_values shape: (1, n_features) for binary classification
    # For XGBoost binary, shap_values may return array for class 1 directly,
    # or a list of [class_0, class_1] arrays. Handle both cases.
    if isinstance(shap_values, list):
        # Use class 1 (failure) SHAP values
        sv = shap_values[1][0]
    elif shap_values.ndim == 2:
        sv = shap_values[0]
    else:
        sv = shap_values

    explanations = []
    for i, feature_name in enumerate(FEATURE_ORDER):
        explanations.append({
            "feature": feature_name,
            "impact": round(float(sv[i]), 4),
            "value": round(float(X[0, i]), 4),
        })

    # Sort by absolute SHAP value (most impactful first)
    explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return explanations


def _generate_natural_explanation(
    explanations: List[Dict[str, Any]],
    risk_level: str,
) -> str:
    """
    Generate a human-readable natural language explanation
    based on the top SHAP contributing features.

    Example: "Failure risk is high mainly due to elevated Engine Temperature
              and abnormal Vibration Level."
    """
    # Take the top contributors that increase failure risk
    top_positive = [e for e in explanations if e["impact"] > 0.01][:3]

    if not top_positive:
        return "All sensor readings are within normal operating parameters."

    risk_label = risk_level.lower()
    feature_phrases = []

    for exp in top_positive:
        label = FEATURE_LABELS.get(exp["feature"], exp["feature"])
        impact = exp["impact"]

        if exp["feature"] == "engine_temp":
            feature_phrases.append(f"elevated {label}")
        elif exp["feature"] == "oil_pressure":
            feature_phrases.append(f"low {label}")
        elif exp["feature"] == "vibration":
            feature_phrases.append(f"abnormal {label}")
        elif exp["feature"] == "battery_voltage":
            feature_phrases.append(f"low {label}")
        elif exp["feature"] == "rpm":
            feature_phrases.append(f"high {label}")
        elif exp["feature"] == "mileage":
            feature_phrases.append(f"high {label}")
        else:
            feature_phrases.append(f"unusual {label}")

    if len(feature_phrases) == 1:
        drivers = feature_phrases[0]
    elif len(feature_phrases) == 2:
        drivers = f"{feature_phrases[0]} and {feature_phrases[1]}"
    else:
        drivers = f"{', '.join(feature_phrases[:-1])}, and {feature_phrases[-1]}"

    return f"Failure risk is {risk_label} mainly due to {drivers}."


def predict_failure(
    features: Dict[str, float],
    explain: bool = False,
) -> Dict[str, Any]:
    """
    Run the ML prediction pipeline.

    Parameters
    ----------
    features : dict
        Must contain keys: engine_temp, oil_pressure, rpm,
        vibration, battery_voltage, mileage
    explain : bool
        If True, compute SHAP explanations for the prediction.

    Returns
    -------
    dict with:
        failure_probability  (float 0-1)
        prediction           (0 or 1)
        risk_level           ("Low" | "Medium" | "High")
        sensor_flags         (list of triggered domain rules)
        threshold_used       (float)
        explanations         (list, only when explain=True)
        natural_explanation  (str, only when explain=True)
        suppressed_by_rules  (bool, only when explain=True and suppressed)
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
    suppressed = False

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
            suppressed = True

    # Risk classification uses raw probability regardless of domain filter
    risk_level = classify_risk(failure_probability)

    result = {
        "failure_probability": failure_probability,
        "prediction": prediction,
        "risk_level": risk_level,
        "sensor_flags": sensor_flags,
        "threshold_used": singleton.threshold,
    }

    # ─── SHAP Explanation (only when requested) ───
    if explain:
        start = time.time()

        shap_explanations = _compute_shap_explanations(X, singleton)
        natural_text = _generate_natural_explanation(shap_explanations, risk_level)

        elapsed_ms = (time.time() - start) * 1000
        logger.info(f"⚡ SHAP explanation computed in {elapsed_ms:.1f}ms")

        result["explanations"] = shap_explanations
        result["natural_explanation"] = natural_text
        result["shap_base_value"] = round(
            float(
                singleton.shap_explainer.expected_value[1]
                if isinstance(singleton.shap_explainer.expected_value, (list, np.ndarray))
                else singleton.shap_explainer.expected_value
            ),
            4,
        )

        # Mark if domain rules suppressed the prediction
        if suppressed:
            result["suppressed_by_rules"] = True
            result["suppression_note"] = (
                "Note: This prediction was suppressed by safety rules. "
                "No domain rule threshold was breached despite elevated ML probability."
            )

    return result


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
